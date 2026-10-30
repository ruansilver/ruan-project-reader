@RestController
public class OrderController {
    @Autowired OrderService orderService;

    @PostMapping("/orders")
    public Result<Long> create(@RequestBody CreateOrderReq req) {
        Long id = orderService.create(req);
        return Result.ok(id);
    }
}
