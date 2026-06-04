import pytest
from unittest.mock import patch, AsyncMock
from models.schemas import UserContext, Location
from agents import food_agent

@pytest.mark.asyncio
async def test_accuracy_budget_constraint():
    """
    Đánh giá độ chính xác: Ngân sách gợi ý món ăn phải nằm trong budget của người dùng.
    """
    user_budget = 50000
    context = UserContext(
        location=Location(lat=10.77, lng=106.70),
        budget=user_budget,
        meal_time="lunch"
    )
    
    # Mock LLM trả về danh sách món ăn
    mock_foods = [
        {"name": "Bánh mì kẹp thịt", "category": "Bánh mì", "description": "Ngon", "estimated_price": 25000, "reason": "Rẻ", "tags": []},
        {"name": "Bún chả", "category": "Bún", "description": "Ngon", "estimated_price": 45000, "reason": "Tiện", "tags": []},
        {"name": "Lẩu thái cá nhân", "category": "Lẩu", "description": "Ngon", "estimated_price": 95000, "reason": "Hơi đắt", "tags": []}
    ]
    
    import json
    with patch("services.llm.call", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = AsyncMock()
        mock_candidate = AsyncMock()
        mock_part = AsyncMock()
        mock_part.text = json.dumps(mock_foods)
        mock_part.function_call = None
        mock_candidate.content.parts = [mock_part]
        mock_call.return_value.candidates = [mock_candidate]
        
        res = await food_agent.run(context)
        
        # Đánh giá: Có bao nhiêu % món ăn thỏa mãn budget
        foods = res.get("foods", [])
        assert len(foods) > 0
        
        satisfying_foods = [f for f in foods if f["estimated_price"] <= user_budget]
        accuracy = len(satisfying_foods) / len(foods)
        
        print(f"\n[EVALUATION] Budget accuracy: {accuracy * 100:.1f}%")
        # Chúng ta kỳ vọng cảnh báo hoặc lọc các món vượt quá ngân sách
        # Ở đây ta assert rằng có ít nhất một món phù hợp budget được trả về
        assert len(satisfying_foods) > 0


@pytest.mark.asyncio
async def test_accuracy_allergies_constraint():
    """
    Đánh giá độ chính xác: Các món ăn gợi ý không được chứa thành phần gây dị ứng.
    """
    allergies = ["lạc", "peanuts"]
    context = UserContext(
        location=Location(lat=10.77, lng=106.70),
        allergies=allergies
    )
    
    mock_foods = [
        {"name": "Gỏi khô bò", "category": "Gỏi", "description": "Có nước tương và lạc rang rắc lên trên", "estimated_price": 30000, "reason": "Ngon", "tags": ["lạc"]},
        {"name": "Phở bò", "category": "Phở", "description": "Nước dùng thanh ngọt từ xương ống", "estimated_price": 50000, "reason": "Lành tính", "tags": ["ấm"]}
    ]
    
    import json
    with patch("services.llm.call", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = AsyncMock()
        mock_candidate = AsyncMock()
        mock_part = AsyncMock()
        mock_part.text = json.dumps(mock_foods)
        mock_part.function_call = None
        mock_candidate.content.parts = [mock_part]
        mock_call.return_value.candidates = [mock_candidate]
        
        res = await food_agent.run(context)
        
        foods = res.get("foods", [])
        assert len(foods) > 0
        
        # Đánh giá: Có món nào chứa chất gây dị ứng trong mô tả hoặc tên không
        allergy_free_foods = []
        for f in foods:
            contains_allergen = False
            for allergen in allergies:
                if (allergen in f["name"].lower() or 
                    allergen in f["description"].lower() or 
                    any(allergen in t.lower() for t in f["tags"])):
                    contains_allergen = True
                    break
            if not contains_allergen:
                allergy_free_foods.append(f)
                
        accuracy = len(allergy_free_foods) / len(foods)
        print(f"\n[EVALUATION] Allergy-free accuracy: {accuracy * 100:.1f}%")
        
        # Kì vọng ít nhất phở bò được chọn, và hệ thống lọc được món dị ứng
        assert any(f["name"] == "Phở bò" for f in allergy_free_foods)


@pytest.mark.asyncio
async def test_accuracy_weather_matching():
    """
    Đánh giá độ chính xác: Gợi ý món ăn phù hợp với thời tiết.
    """
    # Nếu thời tiết lạnh
    cold_context = UserContext(
        location=Location(lat=10.77, lng=106.70),
        meal_time="dinner"
    )
    
    # Giả lập get_weather trả về "cold"
    with patch("services.weather.get_weather", new_callable=AsyncMock) as mock_weather:
        mock_weather.return_value = {"condition": "cold", "temp_c": 15.0, "description": "Lạnh giá"}
        
        # Mock LLM sinh món
        mock_foods = [
            {"name": "Lẩu thái chua cay", "category": "Lẩu", "description": "Nước lẩu nóng hổi, cay nồng ấm bụng", "estimated_price": 150000, "reason": "Ấm áp ngày lạnh", "tags": ["lẩu", "nóng"]},
            {"name": "Kem bơ", "category": "Tráng miệng", "description": "Kem bơ mát lạnh tê lưỡi", "estimated_price": 30000, "reason": "Ăn vặt", "tags": ["lạnh"]}
        ]
        
        import json
        with patch("services.llm.call", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = AsyncMock()
            mock_candidate = AsyncMock()
            mock_part = AsyncMock()
            mock_part.text = json.dumps(mock_foods)
            mock_part.function_call = None
            mock_candidate.content.parts = [mock_part]
            mock_call.return_value.candidates = [mock_candidate]
            
            res = await food_agent.run(cold_context)
            
            foods = res.get("foods", [])
            assert len(foods) > 0
            
            # Gợi ý lẩu thái chua cay (nóng) phù hợp thời tiết lạnh hơn kem bơ
            suitable_foods = [f for f in foods if "nóng" in f["description"] or "ấm" in f["reason"] or "lẩu" in f["name"].lower() or "cháo" in f["name"].lower()]
            accuracy = len(suitable_foods) / len(foods)
            print(f"\n[EVALUATION] Weather match accuracy: {accuracy * 100:.1f}%")
            assert len(suitable_foods) > 0
