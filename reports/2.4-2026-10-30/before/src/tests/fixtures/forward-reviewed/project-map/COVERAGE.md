# 发现与覆盖

范围：/mnt/ext_drive/workspace/AI workspace/skills/ruan-project-reader/src/tests/fixtures/source 内全部 9 个文件；7 个 Java、1 个 XML、1 个 YAML。当前文件内容 SHA-256 见 ../source-baseline.json。无已提供文件被排除；外部依赖/实现未提供。application.yml 仅可确认声明，不能确认为最终生效配置。
召回探针：未提供，未执行用户独立召回探针。
本轮发现暂时收敛：是
本轮范围整体完成：否

## 入口

| 序号 | 来源位置 | 主体流程 | 总览节点 | 下一步 |
| --- | --- | --- | --- | --- |
| E1 | OrderController.java:5-9 POST /orders | [创建订单](modules/10-创建订单.md) | [A](modules/00-总览.md#A) | 无 |
| E2 | OrderEventListener.java:5-8 @MqListener(order.created) | [订单创建通知](modules/20-订单创建通知.md) | [B](modules/00-总览.md#B) | 无 |
| E3 | OrderTimeoutJob.java:6-15 @Scheduled | [超时关单](modules/30-超时关单.md) | [C](modules/00-总览.md#C) | 无 |

StockClient 的两个 @PostMapping 属于出向 Feign 契约，未误记为本项目服务入口。afterCommit 是创建流程内部回调，放入创建模块；死信仅见配置，没有提供消费入口。

## 汇点

| 序号 | 来源位置 | 定位或孤立候选 | 下一步 |
| --- | --- | --- | --- |
| S1 | OrderService.java:12; StockClient.java:3-4 | [库存扣减](modules/10-创建订单.md#必要规则与源码依据) | 无 |
| S2 | OrderMapper.xml:2-5 | [订单插入](modules/10-创建订单.md#必要规则与源码依据) | 无 |
| S3 | MqProducer.java:6-9 | [消息发布](modules/10-创建订单.md#必要规则与源码依据) | 无 |
| S4 | NotifyService.java:11 | [短信发送](modules/20-订单创建通知.md#必要规则与源码依据) | 无 |
| S5 | OrderMapper.xml:9-11 | [条件关单](modules/30-超时关单.md#必要规则与源码依据) | 无 |
| S6 | StockClient.java:6-7 | [库存释放](modules/30-超时关单.md#必要规则与源码依据) | 无 |

六个汇点都已有归属。归属明确不等于外部副作用成功，边界限制保留在对应模块。

## 发现方法

| 方法或方向 | 适用性 | 扫描范围 | 扫描方法 | 检查对象数 | 未检查区域 | 新增候选数 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 正向入口 | 适用 | 全部 9 文件 | rg -n "Mapping\\|Listener\\|Scheduled\\|Application\\|Bean\\|META-INF\\|cron\\|topic" src/tests/fixtures/source；逐行辨别入口与出向声明 | 9 | 无 | 3 | 计数单位为文件；新增为 E1-E3 三个真实入口，不按命中行计数 |
| 反向汇点 | 适用 | 全部 9 文件 | rg -n "insert\\|update\\|delete\\|send\\|reserve\\|notify\\|rollback\\|transaction\\|retry\\|PAID\\|PENDING\\|CANCEL" src/tests/fixtures/source；全读以补足扣减与释放 | 9 | 无 | 6 | 计数单位为文件；首次登记 S1-S6，DB 读取作为下层候选不当作写副作用 |
| 盲区审查 | 适用 | 全部 9 文件及其声明依赖 | rg --files src/tests/fixtures/source；逐行读全部文件；检索所有 public、注解、接口与配置键 | 9 | 无 | 0 | 提供范围无漏读文件；缺失实现的影响登记于本文件未决，零新增仅限当前可见候选 |

## 交叉复查

| 产生候选的方法或方向 | 交叉复查方法或方向 | 检查范围 | 方法 | 检查对象数 | 新增候选数 | 未检查区域 | 未决去向 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 正向入口与执行体阅读 | 反向汇点归属核查 | 六个已登记副作用汇点 | 从 SQL/Feign/Broker/SmsGateway 效果逆查调用者，再与 E1-E3 比对；不是重跑入口关键字 | 6 | 0 | 无 | 无新增，已知边界未知保留模块未决 |
| 按调用/消息寻找跨流程关系 | 写入对象与读取谓词对照 | insert、selectUnpaidBefore、updateStatus 三个 SQL 定义 | 逐列比对 orders、UNPAID、create_time=NOW()、before=now-30分钟及条件更新 | 3 | 1 | 无 | 新增状态扫描交接，已解释于总览候选第二行 |
| 逆向状态与时间谓词比对 | 正向创建入口回走与结果归属核查 | 创建、通知、超时三个主体 | 从 create 跟到 UNPAID 持久化与消息注册，分别核对消费和扫描条件；再核对 CLOSED 后无其他已提供消费流程 | 3 | 0 | 无 | 新增关系已处置，无额外新候选；运行边界限制仍保留 |

首次汇点归属复查未新增入口，但漏看了状态媒介；针对性修订新增 1 条创建→定时扫描交接，已更新总览与两端模块。之后使用正向入口回走复查，新增为 0。暂时收敛仅针对当前已提供样例，不证明没有遗漏外部装配。

## 未决

| 来源 | 类型 | 问题 | 下一步 | 已尝试方法 | 缺失依据 | 影响 | 重试条件 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 盲区审查 | 限制 | 样例缺构建依赖、启动配置、OrderMapper 接口、实体/异常类型、Broker/MqListener/SmsGateway 实现，无法核实实际装配及隐藏入口。 | 在保持当前已提供范围的前提下标明限制；补充实现时重扫装配、入口和汇点。 | rg --files 全量清点，逐行读完全部文件并检索注解、配置、调用与 SQL | 依赖清单及上述实现、全局事务与配置覆盖规则 | 只证明当前样例静态流程，不证明实际部署范围完整；无运行测试条件 | 材料补充或可核查的运行契约出现 |
