#include <iostream>
#include <unistd.h>

#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <SimpleAmqpClient/SimpleAmqpClient.h>

#include "worker/consumer.hpp"
#include "worker/translation.hpp"

using json = nlohmann::json;

#define AMQP_DEFAULT_CONSUMER_TAG           ("")
#define AMQP_DEFAULT_NO_LOCAL               (true)
#define AMQP_DEFAULT_NO_ACK                 (false)
#define AMQP_DEFAULT_EXCLUSIVE              (false)
#define AMQP_DEFAULT_MESSAGE_PREFETCH_COUNT (1)
#define AMQP_DEFAULT_TIMEOUT                (1000) // milliseconds

AmqpConsumer::AmqpConsumer(std::string   aHost,
			   std::uint16_t aPort,
			   std::string   aQueue,
			   std::string   aUsername,
			   std::string   aPassword) {
  mHost     = aHost;
  mPort     = aPort;
  mQueue    = aQueue;
  mUsername = aUsername;
  mPassword = aPassword;
  
  mChannel  = AmqpClient::Channel::Create(mHost, mPort, mUsername, mPassword);
  
  mTag = mChannel->BasicConsume(mQueue,
				AMQP_DEFAULT_CONSUMER_TAG,
				AMQP_DEFAULT_NO_LOCAL,
				AMQP_DEFAULT_NO_ACK,
				AMQP_DEFAULT_EXCLUSIVE,
				AMQP_DEFAULT_MESSAGE_PREFETCH_COUNT);
}

void AmqpConsumer::startBlockingLoop(std::uint16_t interval) {  
  AmqpClient::Envelope::ptr_t envelope;
  
  while (true) {
    if (!mChannel->BasicConsumeMessage(mTag, envelope, AMQP_DEFAULT_TIMEOUT)) {
      continue;
    }
    
    Translation translation = consumeTranslation(envelope);
    
    translation.run();
    postTranslation(translation);
    
    mChannel->BasicAck(envelope);
    
    sleep(interval);
  }
  
}

Translation AmqpConsumer::consumeTranslation(AmqpClient::Envelope::ptr_t & envelope) {
  
  auto message = envelope->Message();
  auto payload = json::parse(message->Body());
  
  auto translation = Translation(payload);
  
  return translation;
}


void AmqpConsumer::postTranslation(Translation translation) {
  CURL *curl;
  CURLcode res;
  
  curl = curl_easy_init();
  
  if(curl) {
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Accept: application/json");
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "charset=UTF-8");

    auto data = translation.getString();
    
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());
    curl_easy_setopt(curl, CURLOPT_URL,translation.getCallbackUrl());

    res = curl_easy_perform(curl);
    
    if(res != CURLE_OK) {
      fprintf(stderr, "curl_easy_perform() failed: %s\n",
	      curl_easy_strerror(res));
    }
    
    curl_easy_cleanup(curl);
  }
}
