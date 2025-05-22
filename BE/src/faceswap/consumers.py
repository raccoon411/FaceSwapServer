import json
import base64
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio

class FaceSwapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connection established")
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close(code=4003)
            return
        
        # Accept the connection
        self.user = self.scope["user"]
        self.room_name = f"faceswap_{self.user.id}"
        self.room_group_name = f"faceswap_{self.user.id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected as {self.user.username}'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                # Parse the JSON data
                data = json.loads(text_data)
                
                if data.get('type') == 'video_frame':
                    # Get the base64 encoded image
                    base64_image = data.get('frame')
                    if base64_image:
                        # Remove the data URL prefix if present
                        if ',' in base64_image:
                            base64_image = base64_image.split(',')[1]
                        
                        # Decode the base64 image
                        image_bytes = base64.b64decode(base64_image)
                        
                        # Convert to numpy array
                        np_arr = np.frombuffer(image_bytes, np.uint8)
                        
                        # Decode the image
                        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                        
                        # Convert to grayscale
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Convert back to BGR for encoding
                        gray_frame_bgr = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
                        
                        # Encode the processed image to JPEG
                        _, buffer = cv2.imencode('.jpg', gray_frame_bgr)
                        
                        # Convert to base64
                        processed_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        # Send back the processed frame
                        await self.send(text_data=json.dumps({
                            'type': 'processed_frame',
                            'frame': processed_base64
                        }))
                
            except Exception as e:
                print(f"Error processing video frame: {str(e)}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))

    async def process_frame(self, frame_data):
        """Process the frame with face swap algorithm"""
        # Convert base64 to image
        try:
            # Remove the data URL prefix if present
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            # Decode base64 to image
            img_bytes = base64.b64decode(frame_data)
            img_np = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            # Apply face swap processing (placeholder)
            # In a real implementation, you would use your face swap algorithm here
            # For now, we'll just add a simple visual effect
            processed_frame = await self.apply_face_swap(frame)
            
            # Convert back to base64
            _, buffer = cv2.imencode('.jpg', processed_frame)
            processed_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return processed_base64
        
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame_data  # Return original frame on error

    async def store_target_image(self, image_data):
        """Store the target image for face swapping"""
        # This would store the target face image that will be used for swapping
        # For simplicity, we're just storing it in memory here
        # In a real app, you might want to store it in a database or file
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        img_np = np.frombuffer(img_bytes, dtype=np.uint8)
        target_image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        
        # Store the target image in the user's session or a database
        # For this example, we'll just store it as an attribute of the consumer
        self.target_image = target_image
        
        # In a real implementation, you might want to extract facial landmarks here
        # to speed up the face swapping process later

    async def apply_face_swap(self, frame):
        """Apply face swap effect to the frame"""
        # This is a placeholder for the actual face swap algorithm
        # In a real implementation, you would use a proper face swap technique
        
        # Check if we have a target image
        if not hasattr(self, 'target_image'):
            # Apply a simple effect instead (grayscale + edge detection)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Simple placeholder effect - blend with target image
        # In a real app, you'd implement proper face detection and swapping
        try:
            # Resize target image to match frame size
            target_resized = cv2.resize(self.target_image, (frame.shape[1], frame.shape[0]))
            
            # Simple alpha blending (not actual face swap)
            alpha = 0.3
            blended = cv2.addWeighted(frame, 1-alpha, target_resized, alpha, 0)
            
            return blended
        except Exception as e:
            print(f"Error in face swap: {e}")
            return frame
        

         # Channel layer message handlers
    async def chat_message(self, event):
        """Handle messages sent through the channel layer"""
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
