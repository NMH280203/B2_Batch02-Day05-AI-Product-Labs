'use client'

import { useState } from 'react'
import { useChatStore } from '@/store/chatStore'
import { FoodList } from './FoodList'
import { RestaurantList } from './RestaurantList'
import { MapEmbed } from '@/components/map/MapEmbed'

type Tab = 'food' | 'restaurant' | 'map'

export function ResultPanel() {
  const [activeTab, setActiveTab] = useState<Tab>('food')
  const { results } = useChatStore()
  const { foods, restaurants } = results

  const hasFood = foods.length > 0
  const hasRestaurant = restaurants.length > 0

  if (!hasFood && !hasRestaurant) return null

  const tabs: { id: Tab; label: string; count?: number; show: boolean }[] = [
    { id: 'food', label: '🍽️ Món ăn', count: foods.length, show: hasFood },
    { id: 'restaurant', label: '🏪 Quán ăn', count: restaurants.length, show: hasRestaurant },
    { id: 'map', label: '🗺️ Bản đồ', show: hasRestaurant },
  ]

  return (
    <div className="flex flex-col h-full bg-[#0f1117] border-l border-white/10">
      {/* Tabs */}
      <div className="flex border-b border-white/10 shrink-0">
        {tabs.filter((t) => t.show).map((tab) => (
          <button
            key={tab.id}
            id={`result-tab-${tab.id}`}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-3 px-2 text-xs font-medium transition-all ${
              activeTab === tab.id
                ? 'text-orange-400 border-b-2 border-orange-400 bg-orange-500/5'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {tab.label}
            {tab.count ? (
              <span className="ml-1 bg-white/10 text-gray-400 text-[10px] rounded-full px-1.5 py-0.5">
                {tab.count}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {activeTab === 'food' && <FoodList foods={foods} />}
        {activeTab === 'restaurant' && <RestaurantList restaurants={restaurants} />}
        {activeTab === 'map' && <MapEmbed restaurants={restaurants} />}
      </div>
    </div>
  )
}
