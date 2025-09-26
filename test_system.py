#!/usr/bin/env python3
"""
Test script for Shuttle Run Assessment System
This script demonstrates how to use the system programmatically
"""

import requests
import json
import os
import time

def test_upload_endpoint():
    """Test the upload endpoint with a sample request"""
    url = "http://localhost:5000/upload"
    
    # Check if there are any video files in the uploads directory
    upload_dir = "uploads"
    video_files = [f for f in os.listdir(upload_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    if not video_files:
        print("No video files found in uploads directory.")
        print("Please add a video file to test the system.")
        return False
    
    # Use the first video file found
    video_file = video_files[0]
    video_path = os.path.join(upload_dir, video_file)
    
    print(f"Testing with video file: {video_file}")
    
    # Prepare the request
    files = {'video': open(video_path, 'rb')}
    data = {'target_laps': '10'}
    
    try:
        print("Uploading video for analysis...")
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Results: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Upload failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error during upload: {str(e)}")
        return False
    finally:
        files['video'].close()

def test_results_endpoint():
    """Test the results endpoint"""
    url = "http://localhost:5000/results/test_video.mp4"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("✅ Results retrieved successfully!")
            print(f"Results: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Results retrieval failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving results: {str(e)}")
        return False

def test_main_page():
    """Test if the main page loads correctly"""
    url = "http://localhost:5000/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Main page loads successfully!")
            return True
        else:
            print(f"❌ Main page failed to load with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading main page: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Shuttle Run Assessment System")
    print("=" * 50)
    
    # Test 1: Main page
    print("\n1. Testing main page...")
    test_main_page()
    
    # Test 2: Upload endpoint
    print("\n2. Testing upload endpoint...")
    upload_success = test_upload_endpoint()
    
    # Test 3: Results endpoint (only if upload was successful)
    if upload_success:
        print("\n3. Testing results endpoint...")
        test_results_endpoint()
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("\nTo use the system:")
    print("1. Open your browser and go to: http://localhost:5000")
    print("2. Upload a video file with red markers at both endpoints")
    print("3. Set the target number of laps")
    print("4. Click 'Analyze Video' to get results")

if __name__ == "__main__":
    main()

