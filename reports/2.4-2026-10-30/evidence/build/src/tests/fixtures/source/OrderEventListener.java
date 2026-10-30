@Component
public class OrderEventListener {
    @Autowired NotifyService notifyService;

    @MqListener(topic = "order.created")
    public void onCreated(Long orderId) {
        notifyService.sendCreatedNotice(orderId);
    }
}
