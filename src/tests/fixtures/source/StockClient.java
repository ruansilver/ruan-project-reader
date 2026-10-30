@FeignClient(name = "stock-service")
public interface StockClient {
    @PostMapping("/stock/deduct")
    boolean deduct(@RequestParam Long skuId, @RequestParam int qty);

    @PostMapping("/stock/release")
    void release(@RequestParam Long skuId, @RequestParam int qty);
}
