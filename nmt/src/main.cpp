#include <csignal>
#include <iostream>
#include <string>

#include <nlohmann/json.hpp>
#include <curl/curl.h>

#include <SimpleAmqpClient/SimpleAmqpClient.h>

using json = nlohmann::json;

namespace {
  volatile std::sig_atomic_t running = 1;
  
  extern "C" void signal_handler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
      running = 0;
    }
  }
}

#define RABBITMQ_DEFAULT_HOST "localhost"
#define RABBITMQ_DEFAULT_PORT 5672
#define RABBITMQ_DEFAULT_USERNAME "guest"
#define RABBITMQ_DEFAULT_PASSWORD "guest"

#define AMQP_DEFAULT_CONSUMER_TAG ""
#define AMQP_DEFAULT_NO_LOCAL true
#define AMQP_DEFAULT_NO_ACK false
#define AMQP_DEFAULT_EXCLUSIVE false
#define AMQP_DEFAULT_MESSAGE_PREFETCH_COUNT 1

void consumer(std::string const & queue) {
  CURL *curl;
  CURLcode res;
  
  AmqpClient::Envelope::ptr_t envelope;

  auto channel = AmqpClient::Channel::Create(
					     RABBITMQ_DEFAULT_HOST,
					     RABBITMQ_DEFAULT_PORT,
					     RABBITMQ_DEFAULT_USERNAME,
					     RABBITMQ_DEFAULT_PASSWORD);

  auto tag = channel->BasicConsume(
				   queue,
				   AMQP_DEFAULT_CONSUMER_TAG,
				   AMQP_DEFAULT_NO_LOCAL,
				   AMQP_DEFAULT_NO_ACK,
				   AMQP_DEFAULT_EXCLUSIVE,
				   AMQP_DEFAULT_MESSAGE_PREFETCH_COUNT
				   );

  while (running) {
    if (!channel->BasicConsumeMessage(tag, envelope, 1000)) {
      continue;
    }

    auto message = envelope->Message();
    auto payload = json::parse(message->Body());
    
    std::cout << payload.dump() << std::endl;
    std::cout << (std::string) payload["id"] << std::endl;
    std::cout << payload["text"] << std::endl;

    curl = curl_easy_init();
    if(curl) {
      struct curl_slist *headers=NULL;
      headers = curl_slist_append(headers, "Accept: application/json");
      headers = curl_slist_append(headers, "Content-Type: application/json");
      
      curl_easy_setopt(curl, CURLOPT_URL, "http://127.0.0.1:5000/");
      curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.dump().c_str());
      curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
      res = curl_easy_perform(curl);
      
      if(res != CURLE_OK)
	fprintf(stderr, "curl_easy_perform() failed: %s\n",
		curl_easy_strerror(res));
 
      curl_easy_cleanup(curl);
    }
    
    channel->BasicAck(envelope);
  }
  channel->BasicCancel(tag);
}

int main(int argc, char const * const argv[]) {
  std::signal(SIGINT, signal_handler);
  std::signal(SIGTERM, signal_handler);
  
  consumer("machine-translations");

  return 0;
}
