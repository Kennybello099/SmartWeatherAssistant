# ai_assistant.py
import requests
import sys
import time
import speech_recognition as sr
import pyttsx3
import serial
from datetime import datetime, timedelta
from typing import Optional, Dict
from config import Config

class AIAssistant:
    """Voice-enabled Real-Time AI Assistant with SerpAPI and Arduino sensor data."""
    
    def __init__(self, arduino_port: str = "COM3", baud_rate: int = 9600):
        """Initialize the AI Assistant with configuration, event log, voice, and Arduino."""
        self.config = Config()
        self.event_log: Dict[str, str] = {}  # For events
        self.temp_data: list = []  # List to store sensor readings with timestamps
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        self.name = None  # Store the user's name
        
        # Initialize Arduino serial connection
        try:
            self.arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
            time.sleep(2)  # Wait for connection to establish
            #print(f"Connected to Arduino on {arduino_port}")
            #self.speak("Connected to Arduino.")
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.arduino = None
            self.speak("Failed to connect to Arduino. Proceeding without it.")
        
        # Debug config initialization
        print(f"Config initialized: DeepInfra Key: {self.config.deepinfra_api_key[:5]}..., SerpAPI Key: {self.config.serpapi_key[:5]}...")
        #self.speak("AI Assistant initialized. Say 'exit' to quit.")

    def test_api_connection(self, model: str = None) -> str:
        """Test connectivity to the DeepInfra API."""
        model = model or self.config.default_model
        headers = {"Authorization": f"Bearer {self.config.deepinfra_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, world!"}],
            "max_tokens": 10
        }
        try:
            response = requests.post(self.config.api_url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            print("API connection successful!")
            print("Test response:", response.json())
            #return "Connection test passed."
        except requests.exceptions.HTTPError as e:
            return f"API test failed: {e} - Details: {e.response.text}"
        except Exception as e:
            return f"Connection test error: {str(e)}"

    def fetch_realtime_data(self, query: str) -> Optional[str]:
        """Fetch real-time data using SerpAPI with tailored query handling."""
        if not self.config.serpapi_key or "your_serpapi_key_here" in self.config.serpapi_key:
            return "Error: Please set a valid SerpAPI key in Config for real-time data."

        query_lower = query.lower()
        if "weather" in query_lower:
            refined_query = f"current weather {query.replace('weather', '').strip()}"
        elif "what’s happening" in query_lower or "current events" in query_lower:
            refined_query = f"latest news {query.replace('what’s happening', '').replace('current events', '').strip()}"
        elif "now" in query_lower or "real time" in query_lower:
            refined_query = f"real-time {query}"
        else:
            refined_query = query

        params = {
            "q": refined_query,
            "api_key": self.config.serpapi_key,
            "num": 3,
            "tbm": "nws" if "news" in query_lower else None
        }
        try:
            response = requests.get(self.config.serpapi_url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if "organic_results" in result and result["organic_results"]:
                snippets = [r.get("snippet", "No snippet available.") for r in result["organic_results"][:3]]
                if "weather" in query_lower:
                    return f"Current weather info: {snippets[0]}"
                elif "news" in query_lower or "what’s happening" in query_lower or "current events" in query_lower:
                    return f"Latest updates: {'; '.join(snippets)}"
                else:
                    return f"Real-time info: {'; '.join(snippets)}"
            return "No real-time data found."
        except requests.exceptions.HTTPError as e:
            return f"Real-time fetch failed: {e} - Details: {e.response.text}"
        except Exception as e:
            return f"Error fetching real-time data: {str(e)}"

    def read_sensor_data(self) -> Optional[Dict[str, float]]:
        """Read temperature and humidity data from Arduino."""
        if self.arduino and self.arduino.in_waiting:
            try:
                data = self.arduino.readline().decode().strip()
                if data:
                    data = data.replace('\r', '').replace('\n', '')
                    values = data.split(',')
                    
                    if len(values) >= 3:
                        temperature_c = float(values[0].strip())
                        temperature_f = float(values[1].strip())
                        humidity = float(values[2].strip())
                        
                        date_key = datetime.now().strftime("%B %d, %Y")
                        self.temp_data.append({
                            "timestamp": datetime.now().isoformat(),
                            "temperature_c": temperature_c,
                            "temperature_f": temperature_f,
                            "humidity": humidity,
                            "date": date_key
                        })
                        if len(self.temp_data) > 500:
                            self.temp_data = self.temp_data[-500:]
                        
                        return {
                            "temperature_c": temperature_c,
                            "temperature_f": temperature_f,
                            "humidity": humidity,
                            "date": date_key
                        }
                    else:
                        print(f"Invalid data format: {values}")
            except ValueError as e:
                print(f"Sensor reading error: could not convert string to float - {e}")
            except Exception as e:
                print(f"Sensor reading error: {e}")
        return None

    def handle_local_query(self, text: str) -> Optional[str]:
        """Handle local queries including date, time, events, and sensor data."""
        text_lower = text.lower().strip("¿?!")
        
        if "date" in text_lower or "today" in text_lower:
            if "what is the date" in text_lower or "today's date" in text_lower:
                return datetime.now().strftime("Today is %B %d, %Y.")
        
        if "time" in text_lower:
            if "what time is it" in text_lower or "current time" in text_lower:
                return datetime.now().strftime("The current time is %I:%M %p.")
        
        if "event" in text_lower:
            if "add event" in text_lower:
                parts = text.split("on")
                if len(parts) > 1:
                    event_desc = parts[0].replace("add event", "").strip()
                    event_date = parts[1].strip()
                    self.event_log[event_date] = event_desc
                    return f"Event '{event_desc}' added for {event_date}."
                return "Please specify the event and date, for example, 'Add event meeting on April 5, 2025'."
            elif "what events" in text_lower or "list events" in text_lower:
                if self.event_log:
                    return "Events:\n" + "\n".join(f"{date}: {desc}" for date, desc in self.event_log.items())
                return "No events logged yet."
        
        if "days until" in text_lower or "days from" in text_lower:
            try:
                target_date_str = text_lower.split("until")[-1].split("from")[-1].strip()
                target_date = datetime.strptime(target_date_str, "%B %d, %Y")
                days_diff = (target_date - datetime.now()).days
                if "until" in text_lower:
                    return f"There are {days_diff} days until {target_date_str}." if days_diff >= 0 else f"{target_date_str} was {-days_diff} days ago."
                return f"{target_date_str} was {days_diff} days ago." if days_diff >= 0 else f"There are {-days_diff} days until {target_date_str}."
            except ValueError:
                return "Please specify a valid date, for example, 'days until April 10, 2025'."

        # Handle temperature and humidity query
        if "temperature" in text_lower and "humidity" in text_lower and "on" in text_lower:
            try:
                date_str = text_lower.split("on")[-1].strip()
                date_key = datetime.strptime(date_str, "%B %d, %Y").strftime("%B %d, %Y")
                latest_data = None
                for entry in reversed(self.temp_data):
                    if entry["date"] == date_key:
                        latest_data = entry
                        break
                if latest_data:
                    return f"On {date_key}, the temperature is {latest_data['temperature_c']:.1f} degrees Celsius and the humidity is {latest_data['humidity']:.1f} percent."
                return f"No sensor data available for {date_key}."
            except ValueError:
                return "Please specify a valid date, for example, 'What’s the temperature and humidity on April 10, 2025?'"
        
        return None

    def ask_ai_question(self, text: str, max_tokens: int = 100, retries: int = 3, model: str = None) -> str:
        """Query the DeepInfra API with retries and model fallback."""
        model = model or self.config.default_model
        headers = {"Authorization": f"Bearer {self.config.deepinfra_api_key}", "Content-Type": "application/json"}
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": text}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        attempt = 0
        while attempt < retries:
            try:
                response = requests.post(self.config.api_url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                result = response.json()
                print("Raw API response:", result)
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"].strip()
                    if answer.endswith("...") and len(answer) > 10:
                        answer = answer[:-3] + "."
                    return answer
                return f"Error: Unexpected response format - {result}"
            except requests.exceptions.HTTPError as e:
                error_code = e.response.status_code
                if error_code == 429:
                    print(f"Rate limit hit, retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                elif error_code == 404 and model != self.config.fallback_model:
                    print(f"Model {model} not found, switching to fallback: {self.config.fallback_model}")
                    return self.ask_ai_question(text, max_tokens, retries, model=self.config.fallback_model)
                else:
                    return f"HTTP Error: {e} - Details: {e.response.text}"
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}/{retries}, retrying...")
            except Exception as e:
                return f"Unexpected Error: {str(e)}"
            attempt += 1
        return "Error: All retries failed."

    def listen(self) -> Optional[str]:
        """Listen to voice input and convert it to text."""
        self.read_sensor_data()  # Read sensor data before listening
        with self.microphone as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now.")
            self.speak("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text.strip()
            except sr.WaitTimeoutError:
                print("No speech detected within timeout.")
                self.speak("I didn't hear anything. Please try again.")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio.")
                self.speak("Sorry, I couldn’t understand you. Please try again.")
                return None
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                self.speak(f"Speech recognition error: {str(e)}")
                return None

    def speak(self, text: str):
        """Convert text to speech and output it."""
        self.engine.say(text)
        self.engine.runAndWait()

    def run(self):
        """Run the main loop of the AI Assistant with voice interaction and Arduino data."""
        #print(f"Welcome to the Smart Weather AI Assistant (Powered by {self.config.default_model})!")
        self.speak(f"Welcome to the Smart Weather AI Assistant. Today is {datetime.now().strftime('%B %d, %Y')}. You can ask me anything related to weather or something to begin, else say 'exit' to quit.")
        #print("Features: Real-time info (weather, news, events), date/time queries, events (e.g., 'Add event meeting on April 5, 2025'), Arduino sensor data (e.g., 'What’s the temperature and humidity on April 1, 2025?').")
        #print("Examples: 'What’s the weather in London today?', 'What’s the temperature and humidity on April 1, 2025?', 'What time is it?'")
        #print("Get API keys from: https://deepinfra.com/dashboard/api | https://serpapi.com/\n")
        
        print("Testing API connection...")
        connection_status = self.test_api_connection()
        print(f"Status: {connection_status}")
        #self.speak(f"API connection status: {connection_status}")

        self.speak("Hello! Please tell me your name.")
        while True:
            name_input = self.listen()
            if name_input:
                self.name = name_input.capitalize()
                self.speak(f"Hey {self.name}, Welcome to the Smart Weather AI Assistant. Today is {datetime.now().strftime('%B %d, %Y')}. You can ask me anything related to weather or something to begin, else say 'exit' to quit.")
                break
            else:
                self.speak("I didn’t catch your name. Please try again.")
        


        # Read and speak initial sensor data
        if self.arduino:
            print("Reading initial sensor data...")
            for _ in range(5):  # Try up to 5 times to get initial data
                data = self.read_sensor_data()
                if data:
                    date_key = data["date"]
                    temp_c = data["temperature_c"]
                    humidity = data["humidity"]
                    initial_report = f"On {date_key}, the temperature is {temp_c:.1f} degrees Celsius and the humidity is {humidity:.1f} percent."
                    print(f"Initial AI Response: {initial_report}")
                    self.speak(initial_report)
                    break
                time.sleep(1)  # Wait between attempts
            else:
                print("No initial sensor data received.")
                self.speak("Having trouble reading the sensors. Please check the Arduino connection.")
        
        while True:
            user_input = self.listen()
            
            if user_input is None:
                continue
            
            if user_input.lower() == "exit" or user_input.lower() == "goodbye" :
                print("Goodbye!")
                self.speak(f"Goodbye, {self.name}")
                if self.arduino:
                    self.arduino.close()
                break
            
            max_tokens = 100
            text = user_input
            if "--short" in text.lower():
                max_tokens = 50
                text = text.replace("--short", "").strip()
            elif "--long" in text.lower():
                max_tokens = 200
                text = text.replace("--long", "").strip()
            
            if not text:
                print("No valid input detected.")
                self.speak("Please say something meaningful.")
                continue
            
            local_response = self.handle_local_query(text)
            if local_response:
                print(f"AI Response: {local_response}")
                self.speak(local_response)
                continue
            
            text_lower = text.lower()
            needs_realtime = any(phrase in text_lower for phrase in ["weather", "what’s happening", "now", "real time", "current events"])
            
            if needs_realtime:
                realtime_data = self.fetch_realtime_data(text)
                if "Error" not in realtime_data:
                    if "weather" in text_lower:
                        answer = realtime_data
                    else:
                        enhanced_prompt = f"Using this real-time info: '{realtime_data}', provide a concise answer to: {text}"
                        answer = self.ask_ai_question(enhanced_prompt, max_tokens=max_tokens)
                else:
                    answer = realtime_data
            else:
                if text_lower.startswith("summarize"):
                    text = f"Provide a concise and accurate summary of the following: {text[9:].strip()}"
                answer = self.ask_ai_question(text, max_tokens=max_tokens)
            
            print(f"AI Response: {answer}")
            self.speak(answer)

if __name__ == "__main__":
    assistant = AIAssistant(arduino_port="COM3")  # Adjust COM port as needed
    assistant.run()