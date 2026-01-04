#!/usr/bin/env python3
"""
Quick start example for weather alert bot.
This demonstrates basic usage without full configuration.
"""

import asyncio
from telegram import Bot


async def test_telegram_connection():
    """Test Telegram bot connection."""
    print("🤖 weather alert bot - quick test\n")
    
    # get credentials
    print("enter your telegram bot token (from @botfather):")
    bot_token = input().strip()
    
    print("\nenter your chat id (from @userinfobot):")
    chat_id = input().strip()
    
    try:
        # test connection
        print("\n⏳ testing connection...")
        bot = Bot(token=bot_token)
        me = await bot.get_me()
        print(f"✅ connected to bot: @{me.username}")
        
        # send test message
        print("\n⏳ sending test message...")
        await bot.send_message(
            chat_id=chat_id,
            text="🎉 *bot is working!*\n\nyour weather alert bot is configured correctly.",
            parse_mode='Markdown'
        )
        print(f"✅ message sent successfully to chat {chat_id}")
        
        print("\n✨ setup successful! you can now configure the full bot.")
        print("\nnext steps:")
        print("  1. copy env.example to .env")
        print("  2. add your tokens to .env")
        print("  3. edit config.yaml with your locations")
        print("  4. run: python main.py --check-now")
        
    except Exception as e:
        print(f"\n❌ error: {e}")
        print("\ntroubleshooting:")
        print("  - verify bot token is correct")
        print("  - verify chat id is correct (should be numbers only)")
        print("  - ensure you've sent /start to your bot first")
        return False
    
    return True


async def quick_weather_check():
    """Quick weather check without full config."""
    print("🌤️ quick weather check\n")
    
    # get api key
    print("enter your openweathermap api key:")
    api_key = input().strip()
    
    print("\nenter city name (e.g., 'london, uk'):")
    city = input().strip()
    
    try:
        from weather_monitor import WeatherMonitor
        
        print("\n⏳ fetching weather forecast...")
        
        monitor = WeatherMonitor(api_key)
        location = {'name': city, 'city': city}
        forecast = monitor.get_forecast(location)
        
        # show tomorrow's summary
        daily = monitor.get_daily_summary(forecast, days_ahead=1)
        
        if daily:
            print(f"\n📅 forecast for tomorrow - {daily['date']}")
            print(f"📍 location: {daily['location_name']}")
            print(f"🌡️  temperature: {daily['temp_min']:.1f}°c - {daily['temp_max']:.1f}°c")
            print(f"💨 max wind: {daily['wind_speed_max']:.1f} km/h")
            if daily['wind_gust_max'] > 0:
                print(f"💨 max gusts: {daily['wind_gust_max']:.1f} km/h")
            print(f"🌧️  precipitation: {daily['precipitation_total']:.1f} mm")
            print(f"☁️  conditions: {', '.join(daily['weather_conditions'])}")
            
            print("\n✅ weather api working correctly!")
        else:
            print("\n⚠️  no forecast data available for tomorrow")
            
    except Exception as e:
        print(f"\n❌ error: {e}")
        print("\ntroubleshooting:")
        print("  - verify api key is correct")
        print("  - check city name spelling")
        print("  - ensure internet connection")
        return False
    
    return True


async def main():
    """Main quick start menu."""
    print("=" * 60)
    print("weather alert bot - quick start")
    print("=" * 60)
    print()
    print("choose an option:")
    print("  1. test telegram bot connection")
    print("  2. test weather api")
    print("  3. both")
    print()
    
    choice = input("enter choice (1/2/3): ").strip()
    print()
    
    if choice == "1":
        await test_telegram_connection()
    elif choice == "2":
        await quick_weather_check()
    elif choice == "3":
        success1 = await test_telegram_connection()
        print("\n" + "=" * 60 + "\n")
        success2 = await quick_weather_check()
        
        if success1 and success2:
            print("\n" + "=" * 60)
            print("✨ all tests passed! your bot is ready to use.")
            print("=" * 60)
    else:
        print("invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 goodbye!")

