@Service
public class OrderService {
    @Autowired StockClient stockClient;
    @Autowired OrderMapper orderMapper;
    @Autowired MqProducer mqProducer;

    @Transactional
    public Long create(CreateOrderReq req) {
        if (req.getQty() <= 0) {
            throw new BizException("数量非法");
        }
        boolean ok = stockClient.deduct(req.getSkuId(), req.getQty());
        if (!ok) {
            throw new BizException("库存不足");
        }
        Order order = new Order(req.getUserId(), req.getSkuId(), req.getQty(), OrderStatus.UNPAID);
        orderMapper.insert(order);
        mqProducer.send("order.created", order.getId());
        return order.getId();
    }
}
