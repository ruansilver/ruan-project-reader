@Component
public class OrderTimeoutJob {
    @Autowired OrderMapper orderMapper;
    @Autowired StockClient stockClient;

    @Scheduled(cron = "0 */5 * * * *")
    public void closeTimeoutOrders() {
        List<Order> list = orderMapper.selectUnpaidBefore(LocalDateTime.now().minusMinutes(30));
        for (Order o : list) {
            int rows = orderMapper.updateStatus(o.getId(), OrderStatus.UNPAID, OrderStatus.CLOSED);
            if (rows == 1) {
                stockClient.release(o.getSkuId(), o.getQty());
            }
        }
    }
}
