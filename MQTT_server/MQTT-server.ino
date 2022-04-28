#include "esp_camera.h"
#include <WiFi.h>
#include "WiFiClientSecure.h"
#include <WebSocketsServer.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

#define CAMERA_MODEL_AI_THINKER

#include "camera_pins.h"
#include "camera_index.h"
#define USE_SERIAL Serial

/************************* WiFi Access Point *********************************/


const char* ssid =      "HOTSPOT";        // Please change ssid & password
const char* password =  "88888888";

#define AIO_SERVER      "io.adafruit.com"
#define AIO_PORT        1883
#define AIO_USERNAME    "toanFam"
#define AIO_KEY         "aio_HJCO27KjksAAXT3yDhfwch0guvFJ"

//WiFiClientSecure client;
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_PORT, AIO_USERNAME, AIO_KEY);

/****************************** Feeds ***************************************/

Adafruit_MQTT_Subscribe button = Adafruit_MQTT_Subscribe(&mqtt, "lgk1910/feeds/button");
Adafruit_MQTT_Publish buttonPublisher = Adafruit_MQTT_Publish(&mqtt, "lgk1910/feeds/button");

Adafruit_MQTT_Publish buzzer = Adafruit_MQTT_Publish(&mqtt, "lgk1910/feeds/buzzer");

/*************************** Sketch Code ************************************/
WebSocketsServer webSocket = WebSocketsServer(8000);

//WiFiServer server(81);
uint8_t client_num;
bool isClientConnected = false;
bool isStreaming = false;

void configCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Select lower framesize if the camera doesn't support PSRAM
  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    config.jpeg_quality = 30; //10-63 lower number means higher quality
    config.fb_count = 2;
  }
  else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void setup_websocket() {
  //    server.begin();
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);

  String IP = WiFi.localIP().toString();
  Serial.println("WebSocket Server IP address: " + IP);
  Serial.println();
}

void shutdown_websocket() {
  //    server.close();
  //    webSocket.close();
  Serial.println("WebSocket Server has been closed!");
  Serial.println();
}

void setup_wifi() {
//  IPAddress staticIP(192, 168, 1, 123);
//  IPAddress gateway(192, 168, 1, 1); // = WiFi.gatewayIP();
//  IPAddress subnet(255, 255, 255, 0); // = WiFi.subnetMask();
//  IPAddress dns1(1, 1, 1, 1);
//  IPAddress dns2(8, 8, 8, 8);
//  
//  if (!WiFi.config(staticIP, dns2, gateway, subnet)) {
//    Serial.print("Wifi configuration for static IP failed!");
//  }

  WiFi.begin(ssid, password);
  Serial.println("");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi " + String(ssid) + " connected.");
  //    Serial.println(WiFi.localIP());
}


void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {

  switch (type) {
    case WStype_DISCONNECTED:
      {
        Serial.printf("[client%u] Disconnected!", num);
        Serial.println();
        client_num = num;
        if (num == 0){
          isClientConnected = false;
          buttonPublisher.publish(0);
          if (isStreaming == true){
            isStreaming = false;
            }
        }
      }
      break;
    case WStype_CONNECTED:
      {
        IPAddress ip = webSocket.remoteIP(num);
        Serial.printf("[client%u] Connected from IP address: ", num);
        Serial.println(ip);
        client_num = num;
        isClientConnected = true;
//        buzzer.publish(1);
//        delay(50);
//        buzzer.publish(0);
//        delay(50);
//        buzzer.publish(1);
//        delay(50);
//        buzzer.publish(0);
      }
      break;
    case WStype_TEXT: // When client send request as text
//      {
//        String receivedPayload = (char*)payload;
//
//        if (receivedPayload == "START") {
//          isStreaming = true;
//          Serial.println(receivedPayload);
//          //            webSocket.sendTXT(num, payload); // Announce data got from client
//        }
//        else if (receivedPayload == "STOP") {
//          isStreaming = false;
//          Serial.println(receivedPayload);
//        }
//      }
      break;
    case WStype_BIN:
    case WStype_ERROR:
    case WStype_FRAGMENT_TEXT_START:
    case WStype_FRAGMENT_BIN_START:
    case WStype_FRAGMENT:
    case WStype_FRAGMENT_FIN:
      break;
  }
}
void setup() {
  Serial.begin(115200);

  setup_wifi();
  configCamera();
  setup_websocket();
  button.setCallback(callbackButton);

  mqtt.subscribe(&button);

}


void callbackButton(char *data, uint16_t len) {
  Serial.print(F("Button mode: "));
  Serial.println(data);
  String readbutton = data;
  if (readbutton == "1") {
    Serial.println("START");
    webSocket.broadcastTXT("START");
    isStreaming = true;
  } else if (readbutton == "0"){
    webSocket.broadcastTXT("STOP");
    isStreaming = false;
  }
}


void loop() {
  MQTT_connect();
  webSocket.loop();

  if (isClientConnected == true && isStreaming == true) {
    //capture a frame
    Serial.println("Sending images");
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Frame buffer could not be acquired");
      return;
    }
    webSocket.broadcastBIN(fb->buf, fb->len); // Broadcast can opened in many IPs

    //return the frame buffer back to be reused
    esp_camera_fb_return(fb);
    mqtt.processPackets(50); 
  }else{
    mqtt.processPackets(50);  
  }
}

// Function to connect and reconnect as necessary to the MQTT server.
// Should be called in the loop function and it will take care if connecting.
void MQTT_connect() {
  int8_t ret;

  // Stop if already connected.
  if (mqtt.connected()) {
    return;
  }

  Serial.print("Connecting to MQTT... ");

  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds...");
    mqtt.disconnect();
    delay(5000);  // wait 5 seconds
    retries--;
    if (retries == 0) {
      while (1);
    }
  }

  buzzer.publish(1);
  delay(100);
  buzzer.publish(0);
  Serial.println("MQTT Connected!");
}
