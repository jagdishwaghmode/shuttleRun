from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2
import numpy as np
import os
import json
from datetime import datetime
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/results', exist_ok=True)

class ShuttleRunAnalyzer:
    def __init__(self):
        self.endpoints = []
        self.lap_times = []
        self.total_laps = 0
        self.distance = 0
        self.distance_pixels = 0
        self.distance_meters = 0
        self.pixels_per_meter = 0
        
    def detect_endpoints(self, frame):
        """Detect endpoints using color detection or manual selection"""
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define range for red color (common for cones/markers)
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        
        # Create mask for red color
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        endpoints = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small contours
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                endpoints.append((center_x, center_y))
        
        return endpoints
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points in pixels"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calibrate_distance(self, known_distance_meters=20):
        """Calibrate pixel to meter conversion using standard shuttle run distance"""
        # Standard shuttle run distance is 20 meters (10 meters each way)
        if self.distance_pixels > 0:
            self.pixels_per_meter = self.distance_pixels / known_distance_meters
            self.distance_meters = self.distance_pixels / self.pixels_per_meter
            return self.distance_meters
        return 0
    
    def calculate_actual_distance_from_video(self, video_path):
        """Calculate actual distance by analyzing video content and known reference objects"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            # Get first frame
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return None
            
            # Try to detect reference objects or use video dimensions for estimation
            height, width = frame.shape[:2]
            
            # Method 1: Try to detect human figure for scale reference
            # Average human height is ~1.7m, we can use this as reference
            human_height_pixels = self.detect_human_height(frame)
            
            if human_height_pixels > 0:
                # Use human height as reference (average 1.7m)
                pixels_per_meter = human_height_pixels / 1.7
                actual_distance = self.distance_pixels / pixels_per_meter
                cap.release()
                return actual_distance
            
            # Method 2: Use video field of view estimation
            # This is a rough estimation based on typical camera angles
            # For a standard phone camera at 1.5m height, 2m distance from track
            estimated_pixels_per_meter = width / 15  # Rough estimation for typical setup
            actual_distance = self.distance_pixels / estimated_pixels_per_meter
            
            cap.release()
            return actual_distance
            
        except Exception as e:
            print(f"Error calculating actual distance: {str(e)}")
            return None
    
    def detect_human_height(self, frame):
        """Detect human figure and estimate height in pixels"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use background subtraction to find moving objects
            # This is a simplified approach - in practice, you'd use more sophisticated methods
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask for skin color detection (simplified)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get largest contour (likely the person)
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 1000:  # Filter small detections
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    return h  # Return height in pixels
            
            return 0
            
        except Exception as e:
            print(f"Error detecting human height: {str(e)}")
            return 0
    
    def track_athlete_movement(self, video_path, target_laps=10, known_distance_meters=20):
        """Process video to track athlete movement and calculate lap times"""
        try:
            print(f"Opening video: {video_path}")
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                print("Error: Could not open video file")
                return {"error": "Could not open video file"}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            print(f"Video info - FPS: {fps}, Frames: {frame_count}, Duration: {duration:.2f}s")
            
            # Get first frame to detect endpoints
            ret, first_frame = cap.read()
            if not ret:
                print("Error: Could not read first frame")
                return {"error": "Could not read video"}
            
            print("Detecting endpoints...")
            # Detect endpoints in first frame
            self.endpoints = self.detect_endpoints(first_frame)
            print(f"Detected {len(self.endpoints)} endpoints: {self.endpoints}")
            
            if len(self.endpoints) < 2:
                print("Warning: Could not detect at least 2 endpoints")
                # For testing, create dummy endpoints if none detected
                if len(self.endpoints) == 0:
                    h, w = first_frame.shape[:2]
                    self.endpoints = [(w//4, h//2), (3*w//4, h//2)]
                    print(f"Using dummy endpoints: {self.endpoints}")
                else:
                    return {"error": "Could not detect at least 2 endpoints. Please ensure red markers are visible."}
            
            # Calculate distance between endpoints
            self.distance_pixels = self.calculate_distance(self.endpoints[0], self.endpoints[1])
            self.distance = self.distance_pixels  # Keep for backward compatibility
            
            # Calculate actual distance from video analysis
            print("Calculating actual distance from video analysis...")
            actual_distance_from_video = self.calculate_actual_distance_from_video(video_path)
            
            if actual_distance_from_video:
                print(f"Actual distance calculated from video: {actual_distance_from_video:.2f} meters")
                
                # Compare with entered distance
                difference = abs(actual_distance_from_video - known_distance_meters)
                accuracy_percentage = (1 - difference / known_distance_meters) * 100
                
                print(f"Entered distance: {known_distance_meters:.2f} meters")
                print(f"Calculated distance: {actual_distance_from_video:.2f} meters")
                print(f"Difference: {difference:.2f} meters")
                print(f"Accuracy: {accuracy_percentage:.1f}%")
                
                # Use the calculated distance for calibration if it's reasonable
                if accuracy_percentage > 70:  # If accuracy is good, use calculated distance
                    print("Using calculated distance for calibration (good accuracy)")
                    self.distance_meters = actual_distance_from_video
                    self.pixels_per_meter = self.distance_pixels / actual_distance_from_video
                else:
                    print("Using entered distance for calibration (calculated distance seems inaccurate)")
                    self.distance_meters = self.calibrate_distance(known_distance_meters)
            else:
                print("Could not calculate actual distance from video, using entered distance")
                self.distance_meters = self.calibrate_distance(known_distance_meters)
            
            print(f"Final distance: {self.distance_meters:.2f} meters")
            print(f"Calibration: {self.pixels_per_meter:.2f} pixels per meter")
            
            # Reset video to beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Track athlete position
            athlete_positions = []
            current_lap = 0
            lap_start_time = 0
            last_position = None
            direction = 1  # 1 for moving towards endpoint 1, -1 for endpoint 2
            
            frame_number = 0
            processed_frames = 0
            
            print("Starting athlete tracking...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_number / fps
                
                # Simple athlete detection (you can improve this with more sophisticated methods)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Use background subtraction for better athlete detection
                if frame_number == 0:
                    background = gray.copy()
                else:
                    diff = cv2.absdiff(background, gray)
                    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                    
                    # Find contours to detect athlete
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        # Get largest contour (likely the athlete)
                        largest_contour = max(contours, key=cv2.contourArea)
                        if cv2.contourArea(largest_contour) > 500:  # Filter small movements
                            M = cv2.moments(largest_contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                athlete_positions.append((cx, cy, current_time))
                                
                                # Check for lap completion
                                if last_position is not None:
                                    # Check if athlete crossed the line between endpoints
                                    if self.check_lap_completion(last_position, (cx, cy)):
                                        if current_lap == 0:
                                            lap_start_time = current_time
                                        else:
                                            lap_time = current_time - lap_start_time
                                            self.lap_times.append(lap_time)
                                            lap_start_time = current_time
                                        
                                        current_lap += 1
                                        print(f"Lap {current_lap} completed at {current_time:.2f}s")
                                        if current_lap >= target_laps:
                                            break
                                    
                                    last_position = (cx, cy)
                                else:
                                    last_position = (cx, cy)
                
                frame_number += 1
                processed_frames += 1
                
                # Progress update every 100 frames
                if processed_frames % 100 == 0:
                    print(f"Processed {processed_frames} frames...")
            
            cap.release()
            print(f"Video processing completed. Processed {processed_frames} frames")
            
            # Calculate final lap time if athlete didn't complete all laps
            if current_lap < target_laps and lap_start_time > 0:
                final_lap_time = duration - lap_start_time
                self.lap_times.append(final_lap_time)
                current_lap += 1
            
            self.total_laps = current_lap
            
            print(f"Final results - Laps: {self.total_laps}/{target_laps}, Lap times: {self.lap_times}")
            
            # Prepare comparison data
            comparison_data = {}
            if actual_distance_from_video:
                difference = abs(actual_distance_from_video - known_distance_meters)
                accuracy_percentage = (1 - difference / known_distance_meters) * 100
                comparison_data = {
                    "entered_distance": known_distance_meters,
                    "calculated_distance": actual_distance_from_video,
                    "difference": difference,
                    "accuracy_percentage": accuracy_percentage,
                    "calibration_method": "calculated" if accuracy_percentage > 70 else "entered"
                }
            
            return {
                "total_laps": self.total_laps,
                "target_laps": target_laps,
                "lap_times": self.lap_times,
                "distance_pixels": self.distance_pixels,
                "distance_meters": self.distance_meters,
                "distance": self.distance_meters,  # Main distance in meters
                "pixels_per_meter": self.pixels_per_meter,
                "endpoints": self.endpoints,
                "duration": duration,
                "processed_frames": processed_frames,
                "distance_comparison": comparison_data
            }
            
        except Exception as e:
            print(f"Error in track_athlete_movement: {str(e)}")
            return {"error": f"Video processing error: {str(e)}"}
    
    def check_lap_completion(self, pos1, pos2):
        """Check if athlete crossed the line between endpoints"""
        # Simple heuristic: check if athlete moved from one side to the other
        # This is a simplified version - you can improve this logic
        if len(self.endpoints) >= 2:
            endpoint1, endpoint2 = self.endpoints[0], self.endpoints[1]
            
            # Calculate which side of the line each position is on
            def point_side(point, line_start, line_end):
                return ((line_end[0] - line_start[0]) * (point[1] - line_start[1]) - 
                       (line_end[1] - line_start[1]) * (point[0] - line_start[0]))
            
            side1 = point_side(pos1, endpoint1, endpoint2)
            side2 = point_side(pos2, endpoint1, endpoint2)
            
            # If signs are different, athlete crossed the line
            return (side1 * side2) < 0
        
        return False

analyzer = ShuttleRunAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        if file and file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Verify file was saved
            if not os.path.exists(filepath):
                return jsonify({'error': 'Failed to save video file'}), 500
            
            # Get target laps and known distance from form
            target_laps = int(request.form.get('target_laps', 10))
            known_distance = float(request.form.get('known_distance', 20))
            
            print(f"Processing video: {filename}")
            print(f"File size: {os.path.getsize(filepath)} bytes")
            print(f"Target laps: {target_laps}")
            print(f"Known distance: {known_distance} meters")
            
            # Process video
            result = analyzer.track_athlete_movement(filepath, target_laps, known_distance)
            
            # Check if processing was successful
            if 'error' in result:
                return jsonify(result), 400
            
            # Save results
            result['video_filename'] = filename
            result['timestamp'] = datetime.now().isoformat()
            
            with open(f'static/results/{filename}_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"Processing completed successfully for {filename}")
            return jsonify(result)
        
        return jsonify({'error': 'Invalid file format. Please upload MP4, AVI, MOV, or MKV files.'}), 400
    
    except Exception as e:
        print(f"Error in upload_video: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/results/<filename>')
def get_results(filename):
    results_file = f'static/results/{filename}_results.json'
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Results not found'}), 404

@app.route('/test')
def test_endpoint():
    """Test endpoint to verify system is working"""
    return jsonify({
        'status': 'OK',
        'message': 'Shuttle Run Assessment System is running',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_file_size': app.config['MAX_CONTENT_LENGTH']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
