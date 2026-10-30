@Service
public class NotifyService {
    @Autowired SmsGateway smsGateway;
    @Autowired OrderMapper orderMapper;

    public void sendCreatedNotice(Long orderId) {
        Order order = orderMapper.selectById(orderId);
        if (order == null) {
            return;
        }
        smsGateway.send(order.getUserId(), "您的订单已创建");
    }
}
