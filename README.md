# SmartWeatherAssistant
Smart Home Accessibility with Generative AI and IoT
This project leverages generative AI models and Internet of Things (IoT) tools to improve the accessibility of smart home applications for individuals with varying levels of visual abilities. By integrating a DHT11 sensor for temperature and humidity data collection and a generative Text-to-Speech (TTS) model, this system provides real-time environmental feedback without the need for additional screen-reading tools. The project also includes a real-time monitoring and data visualization, making it accessible to users worldwide.

**Features**
IoT Sensor Integration:

Collects temperature and humidity data using a DHT11 sensor.

Transfers data over serial communication to a computer for processing.

**Generative AI for Accessibility:**

Utilizes Edge Text-to-Speech (TTS) to provide real-time audio feedback in multiple languages.

Enhances accessibility for users with visual impairments by eliminating the need for screen-reading tools.

**Cross-Language Support:**

The TTS model supports multiple spoken languages, making the system versatile for global users.

Open-Source and Scalable:

Built using open-source tools and platforms, enabling further innovation and customization.

**How It Works**

Connect the DHT11 Sensor:

Connect VCC to 3.3V or 5V.

Connect GND to ground.

Connect Data to a digital pin on the microcontroller.

Add a pull-up resistor (4.7kΩ to 10kΩ) between Data and VCC.

Install Libraries:

For Arduino: Install the DHT library and a TTS library (Adafruit TTS).

For Raspberry Pi: Install Adafruit_DHT and gTTS (or pyttsx3).

Write Code to Read Data:

Use the DHT library to read temperature and humidity.

Print the data to the Serial Monitor or store it in variables.

Add Text-to-Speech (TTS):

For Arduino: Use a TTS module or send data to a computer for TTS.

For Raspberry Pi: Use gTTS or pyttsx3 to convert sensor data into speech.

Test the System:

Upload the code to the microcontroller or run the Python script.

Verify that the DHT11 collects data and the TTS vocalizes the readings.

**Technologies Used**

**Hardware**:

DHT11 Temperature and Humidity Sensor

Microcontroller ( Arduino)

**Software:**

Edge Text-to-Speech (TTS): A generative AI model for real-time audio feedback.

Serial Communication: For data transfer between the sensor and computer.

AI model: mistralai/Mixtral-8x7B-Instruct-v0.1

**Open-Source Tools:**

Generative AI models from platforms like Hugging Face or OpenAI.

IoT platforms like Arduino IDE or PlatformIO.

**Performance and Innovation**

The system is optimized to run on regular processors, ensuring accessibility for users without high-end hardware.

Performance metrics (e.g., latency, accuracy) are documented for further improvement.

**Innovation Pathways:**

This project serves as a foundation for further innovation in generative AI and IoT pipelines.

Peers at Illinois State University and beyond can build upon this work using open-source models and platforms.

**Getting Started
Prerequisites**
Hardware: DHT11 sensor, microcontroller, 830 Tie-point BreadBoard, and connecting cables.

Software: Python, Arduino IDE, C++, Visual-Studio code.

Libraries: Install required libraries for sensor communication and TTS ( DHT11, serial, pyttsx3, requests, speech_recognition, datetime).


**References**

https://docs.arduino.cc/

https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-an-arduino/

https://pyserial.readthedocs.io/en/latest/

https://www.w3schools.in/python/examples/convert-text-to-speech-in-python-with-pyttsx3

https://www.circuitgeeks.com/arduino-dht11-and-dht22-sensor-tutorial/#google_vignette
