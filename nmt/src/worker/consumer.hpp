#ifndef _CONSUMER_HPP_
#define _CONSUMER_HPP_

#include <string>
#include <cstdint>

#include <SimpleAmqpClient/SimpleAmqpClient.h>

#include "worker/common.hpp"
#include "worker/translation.hpp"

class AmqpConsumer {
public:
  AmqpConsumer(std::string   aHost     = RABBITMQ_DEFAULT_HOST,
	       std::uint16_t aPort     = RABBITMQ_DEFAULT_PORT,
	       std::string   aQueue    = RABBITMQ_DEFAULT_QUEUE,
	       std::string   aUsername = RABBITMQ_DEFAULT_USERNAME,
	       std::string   aPassword = RABBITMQ_DEFAULT_PASSWORD);
  
  ~AmqpConsumer() {};
  
  void startBlockingLoop(std::uint16_t interval);
  
private:  
  std::string   mHost;
  std::uint16_t mPort;
  std::string   mQueue;
  std::string   mUsername;
  std::string   mPassword;
  
  AmqpClient::Channel::ptr_t mChannel;
  std::string                mTag;
  
  Translation consumeTranslation(AmqpClient::Envelope::ptr_t & envelope);
  
  void postTranslation(Translation translation);
};

#endif
