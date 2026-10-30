@Component
public class MqProducer {
    @Autowired Broker broker;

    public void send(String topic, Object payload) {
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                broker.publish(topic, payload);
            }
        });
    }
}
