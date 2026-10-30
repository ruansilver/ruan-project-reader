# 入口、汇点与盲区检索示例

依据：附件《ruan-project-reader Skill 设计规范（2.2）》§4。以下是 **Java / Spring 风格的通用只读 shell 检索示例，不是自动发现扫描器，也不是完整规则库**。须按用户当前授权仓库的真实技术栈、依赖版本、配置方式、源码布局和命名替换。其他技术栈不能直接套用这些名称。

命中是调查线索，不是流程已核实；未命中不是实现不存在。检索后读取真实执行体、配置与调用位置，记录实际检查对象和未检查区域。不能凭匹配文本、方法名或注解单独宣布入口、汇点、叶子或覆盖完成。

## 1. 先确认范围与检索能力

下面假设 shell 中已有 `rg`，且 `ROOT` 指向用户授权的当前源码根目录；替换路径后再执行。命令只读，不切换分支或远端版本。

```sh
ROOT='/替换为用户授权的当前仓库路径'
cd "$ROOT" || exit 1

# 枚举可能有助于识别技术栈、源码和生效配置的文件。
rg --files --hidden -g '!.git/**' \
  -g '*.java' -g '*.kt' -g 'pom.xml' -g '*.gradle' -g '*.gradle.kts' \
  -g '*.yml' -g '*.yaml' -g '*.properties' -g '*.xml' \
  -g '**/META-INF/services/**' -g '**/META-INF/spring/**' \
  -g '**/META-INF/spring.factories'
```

`rg` 的隐藏文件、忽略规则与所给 glob 会影响范围；实际采用的范围和未检查区须明示，不能将默认忽略区当作已检查。工具不可用、目录不在授权范围或命令失败时，记录缺口，使用当前可用的只读检索方式或保留待办，不能把失败当成零结果。

枚举文件数、命中行数不等于已核实对象数。记录采用的方法、实际检查对象数和未检查区域；模块候选“检查对象数”按固定候选表各行数量汇总，见 [check-format.md](check-format.md)。

## 2. 正向入口线索

```sh
# 路由、控制器、消息监听、定时、异步、启动和事件回调。
rg -n --glob '*.java' --glob '*.kt' \
  '@(RestController|Controller|RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|KafkaListener|RabbitListener|JmsListener|Scheduled|Async|EventListener|PostConstruct)|ApplicationRunner|CommandLineRunner|ApplicationListener|SmartLifecycle|SchedulingConfigurer|implements[[:space:]]+(Runnable|Callable)' .

# 函数式路由、程序化任务注册、线程／后台循环等线索。
rg -n --glob '*.java' --glob '*.kt' \
  'RouterFunction|RouterFunctions|scheduleAtFixedRate|scheduleWithFixedDelay|TaskScheduler|ExecutorService|new[[:space:]]+Thread|while[[:space:]]*\(' .

# 配置、自动装配、动态选择和反射，命中后核对实际生效条件。
rg -n --glob '*.java' --glob '*.kt' \
  '@(Bean|Import|ComponentScan|EnableScheduling|EnableAsync|ConfigurationProperties|ConditionalOn[^ (]*)|ServiceLoader|Class\.forName|ImportSelector|BeanDefinitionRegistryPostProcessor' .

# XML／属性可能配置的入口、监听器、任务、自动装配与迁移。
rg -n --hidden -g '!.git/**' \
  --glob '*.xml' --glob '*.yml' --glob '*.yaml' --glob '*.properties' \
  'listener|consumer|scheduler|scheduled|cron|callback|webhook|bean|component-scan|flyway|liquibase|spring\.factories' .

# SPI 与 Spring 注册资源先列文件，再读取实际内容与被注册实现。
rg --files --hidden -g '!.git/**' \
  -g '**/META-INF/services/**' -g '**/META-INF/spring/**' \
  -g '**/META-INF/spring.factories'
```

以上名称只是示例。继承式框架回调、组合注解、函数式处理器、外部容器配置、SQL 迁移、数据库触发器或项目自定义注册表，均须依实际依赖和配置调查；不能因示例没有包含就忽略。迁移与启动执行是否在本轮范围内、什么配置实际启用，须据当前源码与授权事实记录，不凭命名推定。

将已核实入口记录到 COVERAGE.md，并追到主体流程与总览实际节点；尚无归属的入口标未映射，进入待办。

## 3. 反向重要汇点线索

```sh
# 持久化与状态写入：API 名称可能只是普通方法，必须读实现。
rg -n --glob '*.java' --glob '*.kt' --glob '*.xml' --glob '*.sql' \
  '\.(save|saveAll|insert|update|delete|remove|persist|merge|executeUpdate|batchUpdate)[[:space:]]*\(|@(Modifying|Insert|Update|Delete)|(^|[[:space:]])(INSERT[[:space:]]+INTO|UPDATE|DELETE[[:space:]]+FROM)[[:space:]]' .

# 缓存及可能的重要状态变化，补入项目实际的状态字段／状态机 API。
rg -n --glob '*.java' --glob '*.kt' \
  'RedisTemplate|StringRedisTemplate|CacheManager|@(CachePut|CacheEvict)|opsForValue|opsForHash|setStatus|setState|transitionTo' .

# 消息发送、异步交接及事件发布。
rg -n --glob '*.java' --glob '*.kt' \
  'KafkaTemplate|RabbitTemplate|JmsTemplate|StreamBridge|convertAndSend|sendMessage|publishEvent|CompletableFuture|\.submit[[:space:]]*\(' .

# 外部调用与副作用入口，补入真实客户端／适配器符号。
rg -n --glob '*.java' --glob '*.kt' \
  'RestTemplate|WebClient|FeignClient|HttpClient|OkHttpClient|Grpc|ManagedChannel|ProcessBuilder|Files\.(write|delete|move)|FileOutputStream' .
```

从命中的实际重要效果反查调用者、分派、配置和触发流程；对自定义 Repository、DAO、缓存包装器、消息封装或 SDK，用真实符号继续检索并读源码。检索调用者的最小模式例如：

```sh
# 将示例符号替换为已读源码确认的实际符号。
rg -n --fixed-strings 'ActualEffectMethod' .
```

此类文本引用检索不能证明运行时可达性，也不能代替动态调用或框架分派调查。必要时继续向深层追踪，或登记下一调查动作。

每个汇点在 COVERAGE.md 指向模块候选行或正文证据位置，才算已映射；仅“理论可达”不算。找不到归属时登记孤立汇点候选，不直接断言死代码或无入口。

## 4. 盲区审查线索

```sh
# 先看文件布局与命名；命中只提示可能遗漏的流程类别。
rg --files --hidden -g '!.git/**' | \
  rg -i '(^|/)(job|jobs|task|tasks|scheduler|listener|consumer|callback|webhook|migration|migrations|batch|bootstrap|config|integration|adapter)(/|[^/]*)'

# 检查依赖与配置是否暗示未调查的运行机制。
rg -n --hidden -g '!.git/**' \
  --glob 'pom.xml' --glob '*.gradle' --glob '*.gradle.kts' \
  --glob '*.xml' --glob '*.yml' --glob '*.yaml' --glob '*.properties' \
  'kafka|amqp|rabbit|jms|quartz|batch|flyway|liquibase|redis|webflux|websocket|grpc|dubbo|activiti|camunda' .
```

将目录、包名、依赖和配置相互对照：有哪些已使用机制没有对应入口／流程记录？有哪些重要汇点还没有模块证据定位？哪些配置选择、隐式入口、异步交接尚未核实？猜测只用来提问和形成候选，不能直接写成项目事实。给远端的结构摘要仍受外发授权约束。

## 5. 记录与交叉复查

每种适用方法记录**范围 / 可重跑命令或检索模式 / 实际检查对象数量 / 未检查区域**。不要把执行示例命令本身当成查完所有实现，也不要自动把原始命中批量判为已处置。

形成新候选后，按需重查受影响方向，并至少做一次与候选来源不同方向或方法的交叉复查。该复查须零新增，记录新增数（包括 0），且已发现候选均有处置或未决去向，才满足本轮发现暂时收敛的相关条件。重跑同一模式零新增不算交叉复查；完整条件见 [discovery-and-coverage.md](discovery-and-coverage.md)。

本文件只给人工可复跑的通用检索模式，不新增自动扫描器、调用图引擎、强制检索词库或额外完成门槛。
