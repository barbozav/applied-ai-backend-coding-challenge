#include <cstdlib>
#include <string>

#include "worker/common.hpp"
#include "worker/consumer.hpp"

int main(int argc, char const * const argv[]) {
  
  if (argc != 4) {
    fprintf(stderr, "USAGE: ./worker <AMQP_HOST> <AMQP_PORT> <AMQP_QUEUE>\n");
    exit(-1);
  }
  
  std::string   host  = argv[1];
  std::uint16_t port  = atoi(argv[2]);
  std::string   queue = argv[3];
  
  auto consumer = AmqpConsumer(host,
			       port,
			       queue);

  consumer.startBlockingLoop(CONSUMER_DEFAULT_PERIOD);
  
  return 0;
}
