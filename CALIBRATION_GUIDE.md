# Distance Calibration Guide

## 🎯 **Distance Now in Meters!**

The shuttle run assessment system now calculates distances in **meters** instead of pixels, making it much more practical for real-world use.

## How It Works

### Automatic Calibration
The system automatically calibrates pixel distance to real-world meters using a **known distance** that you provide.

### Standard Shuttle Run Distance
- **Default**: 20 meters (10 meters each way)
- **Adjustable**: You can set any known distance from 1-100 meters

## Calibration Process

1. **Set Known Distance**: Enter the actual distance between your endpoints in meters
2. **System Calculation**: The system measures the pixel distance between detected endpoints
3. **Conversion**: It calculates how many pixels equal one meter
4. **Result**: All distances are now displayed in meters

## Example Results

```
Distance Between Endpoints: 20.00 meters
Calibration: 32.0 pixels/meter
```

This means:
- 640 pixels = 20 meters
- 32 pixels = 1 meter
- All future measurements use this calibration

## Setting Up Your Video

### For Accurate Results:
1. **Measure the actual distance** between your shuttle run endpoints
2. **Enter this distance** in the "Known Distance" field
3. **Ensure clear markers** at both endpoints for detection

### Common Shuttle Run Distances:
- **Standard**: 20 meters (10m each way)
- **Short**: 10 meters (5m each way)  
- **Long**: 30 meters (15m each way)
- **Custom**: Any distance you measure

## Calibration Accuracy

The system assumes:
- The camera is positioned perpendicular to the running path
- The endpoints are clearly visible and detectable
- The distance between endpoints is consistent

## Troubleshooting Calibration

### If distance seems wrong:
1. **Check your measurement** - Make sure you measured the actual distance correctly
2. **Verify endpoint detection** - Ensure both endpoints are clearly visible
3. **Camera angle** - Make sure the camera is positioned straight-on, not at an angle
4. **Try different known distance** - If you're unsure, try measuring a different reference distance

### Manual Calibration:
If automatic detection fails, the system uses dummy endpoints based on video dimensions, which may not be accurate. For best results:
- Use clear red markers or cones
- Ensure good lighting
- Keep camera stable and perpendicular

## Benefits of Meter Calibration

✅ **Real-world measurements** - No more guessing pixel distances  
✅ **Consistent results** - Same calibration across different videos  
✅ **Professional accuracy** - Suitable for official assessments  
✅ **Easy comparison** - Compare results across different athletes  
✅ **Standard compliance** - Matches official shuttle run protocols  

The system is now ready for professional shuttle run assessments with accurate meter-based measurements!

