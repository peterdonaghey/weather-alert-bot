"""
Generate markdown samples of different hourly forecast formats for mobile.
Creates a markdown file with multiple format options to preview.
"""

from datetime import datetime, timedelta

# Sample forecast data based on the image
sample_forecasts = [
    {
        "time": datetime(2025, 1, 21, 12, 0),
        "temp": 9,
        "feels_like": 8,
        "wind": 7,
        "precip": 1.9,
        "humidity": 100,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 21, 15, 0),
        "temp": 11,
        "feels_like": 10,
        "wind": 23,
        "precip": 0.2,
        "humidity": 90,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 21, 18, 0),
        "temp": 6,
        "feels_like": 1,
        "wind": 30,
        "precip": 0.2,
        "humidity": 89,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 21, 21, 0),
        "temp": 5,
        "feels_like": 0,
        "wind": 30,
        "precip": 1.2,
        "humidity": 91,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 22, 0, 0),
        "temp": 4,
        "feels_like": 0,
        "wind": 26,
        "precip": 0.4,
        "humidity": 91,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 22, 6, 0),
        "temp": 6,
        "feels_like": 2,
        "wind": 22,
        "precip": 0,
        "humidity": 84,
        "condition": "Clouds",
        "emoji": "☁️"
    },
    {
        "time": datetime(2025, 1, 22, 15, 0),
        "temp": 7,
        "feels_like": 4,
        "wind": 12,
        "precip": 3.4,
        "humidity": 98,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 22, 18, 0),
        "temp": 7,
        "feels_like": 6,
        "wind": 9,
        "precip": 9.0,
        "humidity": 99,
        "condition": "Rain",
        "emoji": "🌧️"
    },
    {
        "time": datetime(2025, 1, 23, 9, 0),
        "temp": 3,
        "feels_like": 2,
        "wind": 7,
        "precip": 4.9,
        "humidity": 98,
        "condition": "Snow",
        "emoji": "🌨️"
    },
]

def format_current():
    """Current format - single line with bullets"""
    lines = []
    lines.append("## Format 1: Current (Single Line with Bullets)")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        line = f"**{time_str}** • 🌡️ {f['temp']:.0f}°({f['feels_like']:.0f}°) • 💨 {f['wind']:.0f}km/h"
        if f['precip'] > 0:
            line += f" • 💧 {f['precip']:.1f}mm"
        line += f" • 💧 {f['humidity']:.0f}% • {f['emoji']} {f['condition']}"
        lines.append(line)
    
    lines.append("")
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        line = f"**{time_str}** • 🌡️ {f['temp']:.0f}°({f['feels_like']:.0f}°) • 💨 {f['wind']:.0f}km/h"
        if f['precip'] > 0:
            line += f" • 💧 {f['precip']:.1f}mm"
        line += f" • 💧 {f['humidity']:.0f}% • {f['emoji']} {f['condition']}"
        lines.append(line)
    
    return "\n".join(lines)


def format_multiline_compact():
    """Multi-line compact - each entry on 2-3 lines"""
    lines = []
    lines.append("## Format 2: Multi-line Compact")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        lines.append(f"**{time_str}** {f['emoji']} {f['condition']}")
        lines.append(f"  🌡️ {f['temp']:.0f}° (feels {f['feels_like']:.0f}°) • 💨 {f['wind']:.0f}km/h")
        if f['precip'] > 0:
            lines.append(f"  💧 {f['precip']:.1f}mm • Humidity {f['humidity']:.0f}%")
        else:
            lines.append(f"  💧 Humidity {f['humidity']:.0f}%")
        lines.append("")
    
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        lines.append(f"**{time_str}** {f['emoji']} {f['condition']}")
        lines.append(f"  🌡️ {f['temp']:.0f}° (feels {f['feels_like']:.0f}°) • 💨 {f['wind']:.0f}km/h")
        if f['precip'] > 0:
            lines.append(f"  💧 {f['precip']:.1f}mm • Humidity {f['humidity']:.0f}%")
        else:
            lines.append(f"  💧 Humidity {f['humidity']:.0f}%")
        lines.append("")
    
    return "\n".join(lines)


def format_vertical_stack():
    """Vertical stack - time and condition on top, details below"""
    lines = []
    lines.append("## Format 3: Vertical Stack")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        lines.append(f"**{time_str}** {f['emoji']} {f['condition']}")
        lines.append(f"  Temp: {f['temp']:.0f}° (feels {f['feels_like']:.0f}°)")
        lines.append(f"  Wind: {f['wind']:.0f} km/h")
        if f['precip'] > 0:
            lines.append(f"  Rain: {f['precip']:.1f} mm")
        lines.append(f"  Humidity: {f['humidity']:.0f}%")
        lines.append("")
    
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        lines.append(f"**{time_str}** {f['emoji']} {f['condition']}")
        lines.append(f"  Temp: {f['temp']:.0f}° (feels {f['feels_like']:.0f}°)")
        lines.append(f"  Wind: {f['wind']:.0f} km/h")
        if f['precip'] > 0:
            lines.append(f"  Rain: {f['precip']:.1f} mm")
        lines.append(f"  Humidity: {f['humidity']:.0f}%")
        lines.append("")
    
    return "\n".join(lines)


def format_icon_first():
    """Icon-first - emoji and condition lead, details follow"""
    lines = []
    lines.append("## Format 4: Icon-First Compact")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        lines.append(f"{f['emoji']} **{time_str}** {f['condition']}")
        detail_line = f"   {f['temp']:.0f}°({f['feels_like']:.0f}°) | {f['wind']:.0f}km/h"
        if f['precip'] > 0:
            detail_line += f" | {f['precip']:.1f}mm | {f['humidity']:.0f}%"
        else:
            detail_line += f" | {f['humidity']:.0f}%"
        lines.append(detail_line)
        lines.append("")
    
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        lines.append(f"{f['emoji']} **{time_str}** {f['condition']}")
        detail_line = f"   {f['temp']:.0f}°({f['feels_like']:.0f}°) | {f['wind']:.0f}km/h"
        if f['precip'] > 0:
            detail_line += f" | {f['precip']:.1f}mm | {f['humidity']:.0f}%"
        else:
            detail_line += f" | {f['humidity']:.0f}%"
        lines.append(detail_line)
        lines.append("")
    
    return "\n".join(lines)


def format_minimal():
    """Minimal - only essential info, very compact"""
    lines = []
    lines.append("## Format 5: Minimal (Essential Only)")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        line = f"**{time_str}** {f['emoji']} {f['temp']:.0f}°"
        if f['precip'] > 0:
            line += f" {f['precip']:.1f}mm"
        line += f" 💨{f['wind']:.0f}"
        lines.append(line)
    
    lines.append("")
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        line = f"**{time_str}** {f['emoji']} {f['temp']:.0f}°"
        if f['precip'] > 0:
            line += f" {f['precip']:.1f}mm"
        line += f" 💨{f['wind']:.0f}"
        lines.append(line)
    
    return "\n".join(lines)


def format_two_column():
    """Two-column style - time/temp on left, details on right"""
    lines = []
    lines.append("## Format 6: Two-Column Style")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        left = f"**{time_str}** {f['emoji']}"
        right_parts = [f"{f['temp']:.0f}°({f['feels_like']:.0f}°)"]
        if f['precip'] > 0:
            right_parts.append(f"{f['precip']:.1f}mm")
        right_parts.append(f"💨{f['wind']:.0f}")
        right_parts.append(f"{f['humidity']:.0f}%")
        right = " • ".join(right_parts)
        lines.append(f"{left}  {right}")
        lines.append(f"  {f['condition']}")
        lines.append("")
    
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        left = f"**{time_str}** {f['emoji']}"
        right_parts = [f"{f['temp']:.0f}°({f['feels_like']:.0f}°)"]
        if f['precip'] > 0:
            right_parts.append(f"{f['precip']:.1f}mm")
        right_parts.append(f"💨{f['wind']:.0f}")
        right_parts.append(f"{f['humidity']:.0f}%")
        right = " • ".join(right_parts)
        lines.append(f"{left}  {right}")
        lines.append(f"  {f['condition']}")
        lines.append("")
    
    return "\n".join(lines)


def format_emoji_dense():
    """Emoji-dense - lots of emojis, minimal text"""
    lines = []
    lines.append("## Format 7: Emoji-Dense")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        line = f"**{time_str}** {f['emoji']} 🌡️{f['temp']:.0f}°"
        if f['precip'] > 0:
            if f['precip'] >= 5:
                line += f" 🌧️🌧️{f['precip']:.1f}mm"
            else:
                line += f" 💧{f['precip']:.1f}mm"
        line += f" 💨{f['wind']:.0f} 💧{f['humidity']:.0f}%"
        lines.append(line)
    
    lines.append("")
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        line = f"**{time_str}** {f['emoji']} 🌡️{f['temp']:.0f}°"
        if f['precip'] > 0:
            if f['precip'] >= 5:
                line += f" 🌧️🌧️{f['precip']:.1f}mm"
            else:
                line += f" 💧{f['precip']:.1f}mm"
        line += f" 💨{f['wind']:.0f} 💧{f['humidity']:.0f}%"
        lines.append(line)
    
    return "\n".join(lines)


def format_smart_wrap():
    """Smart wrap - breaks at logical points for better mobile wrapping"""
    lines = []
    lines.append("## Format 8: Smart Wrap (Logical Breaks)")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        # First line: time, emoji, condition
        line1 = f"**{time_str}** {f['emoji']} {f['condition']}"
        # Second line: temp and feels like with icon
        line2 = f"  🌡️ {f['temp']:.0f}° (feels {f['feels_like']:.0f}°)"
        # Third line: wind, rain (if any), humidity
        line3_parts = [f"💨 {f['wind']:.0f}km/h"]
        if f['precip'] > 0:
            line3_parts.append(f"💧 {f['precip']:.1f}mm")
        line3_parts.append(f"💧 {f['humidity']:.0f}%")
        line3 = " • ".join(line3_parts)
        
        lines.append(line1)
        lines.append(line2)
        lines.append(f"  {line3}")
        lines.append("")
    
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        line1 = f"**{time_str}** {f['emoji']} {f['condition']}"
        line2 = f"  🌡️ {f['temp']:.0f}° (feels {f['feels_like']:.0f}°)"
        line3_parts = [f"💨 {f['wind']:.0f}km/h"]
        if f['precip'] > 0:
            line3_parts.append(f"💧 {f['precip']:.1f}mm")
        line3_parts.append(f"💧 {f['humidity']:.0f}%")
        line3 = " • ".join(line3_parts)
        
        lines.append(line1)
        lines.append(line2)
        lines.append(f"  {line3}")
        lines.append("")
    
    return "\n".join(lines)


def format_condensed_two_line():
    """Condensed two-line - time/condition on top, details below"""
    lines = []
    lines.append("## Format 9: Condensed Two-Line")
    lines.append("")
    lines.append("**⏰ NEXT 48 HOURS (3-hourly breakdown)**")
    lines.append("")
    lines.append("**📅 Wednesday, Jan 21**")
    lines.append("")
    
    for f in sample_forecasts[:4]:
        time_str = f["time"].strftime("%H:%M")
        line1 = f"**{time_str}** {f['emoji']} {f['condition']}"
        line2_parts = [f"🌡️ {f['temp']:.0f}°({f['feels_like']:.0f}°)"]
        if f['precip'] > 0:
            line2_parts.append(f"{f['precip']:.1f}mm")
        line2_parts.append(f"💨{f['wind']:.0f}")
        line2_parts.append(f"{f['humidity']:.0f}%")
        line2 = " • ".join(line2_parts)
        lines.append(line1)
        lines.append(f"  {line2}")
        lines.append("")
    
    lines.append("**📅 Thursday, Jan 22**")
    lines.append("")
    
    for f in sample_forecasts[4:8]:
        time_str = f["time"].strftime("%H:%M")
        line1 = f"**{time_str}** {f['emoji']} {f['condition']}"
        line2_parts = [f"🌡️ {f['temp']:.0f}°({f['feels_like']:.0f}°)"]
        if f['precip'] > 0:
            line2_parts.append(f"{f['precip']:.1f}mm")
        line2_parts.append(f"💨{f['wind']:.0f}")
        line2_parts.append(f"{f['humidity']:.0f}%")
        line2 = " • ".join(line2_parts)
        lines.append(line1)
        lines.append(f"  {line2}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Generate markdown file with all format samples"""
    content = []
    content.append("# Hourly Forecast Format Options")
    content.append("")
    content.append("Preview different formatting styles for mobile Telegram viewports.")
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_current())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_multiline_compact())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_vertical_stack())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_icon_first())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_minimal())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_two_column())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_emoji_dense())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_smart_wrap())
    content.append("")
    content.append("---")
    content.append("")
    
    content.append(format_condensed_two_line())
    content.append("")
    
    with open("hourly_forecast_formats.md", "w") as f:
        f.write("\n".join(content))
    
    print("✓ Generated hourly_forecast_formats.md")


if __name__ == "__main__":
    main()
