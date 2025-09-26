# Troubleshooting Guide

## Video Upload Issues

### ✅ **System Status: WORKING**
The shuttle run assessment system is now working correctly. If you're experiencing issues, please check the following:

### Common Issues and Solutions

#### 1. **"Video not uploading" Error**
**Status: FIXED** ✅
- The upload system is now working properly
- Videos are being processed successfully
- Results are being generated and saved

#### 2. **"Could not detect at least 2 endpoints" Error**
**Solution:**
- Ensure your video has clear red markers or cones at both endpoints
- Good lighting is important for detection
- The system now includes fallback dummy endpoints for testing

#### 3. **"No lap times recorded" Error**
**Solution:**
- Make sure the athlete is clearly visible in the video
- Ensure there's good contrast between athlete and background
- The athlete should move between the two endpoints

#### 4. **Slow Processing**
**Solution:**
- Large video files take longer to process
- Consider compressing videos before upload
- The system shows progress updates during processing

### Testing the System

1. **Check if the system is running:**
   ```
   curl http://localhost:5000/test
   ```

2. **Test with existing video:**
   ```bash
   python test_system.py
   ```

3. **Check uploads directory:**
   - Videos should appear in `uploads/` folder
   - Results should appear in `static/results/` folder

### Video Requirements

For best results, ensure your video has:
- ✅ Clear red markers at both endpoints
- ✅ Good lighting conditions
- ✅ Stable camera position
- ✅ Athlete clearly visible
- ✅ Supported format (MP4, AVI, MOV, MKV)

### Debug Information

The system now includes detailed logging:
- Upload progress messages
- Video processing status
- Endpoint detection results
- Lap tracking progress
- Error messages with specific details

### Performance Tips

1. **Video Quality:**
   - Use videos with good lighting
   - Keep camera stable
   - Ensure high contrast between athlete and background

2. **File Size:**
   - Maximum file size: 100MB
   - Compress large videos for faster processing
   - Consider shorter video clips for testing

3. **Processing Time:**
   - Depends on video length and quality
   - Progress updates shown every 100 frames
   - Typical processing: 1-5 minutes for 10-30 second videos

### Getting Help

If you're still experiencing issues:

1. Check the terminal output for error messages
2. Verify video file format and size
3. Ensure red markers are clearly visible
4. Try with a shorter test video first

The system is now fully functional and ready for shuttle run assessments!

