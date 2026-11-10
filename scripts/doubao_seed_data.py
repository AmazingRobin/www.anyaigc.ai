"""Doubao Seed model facts verified against the AnyAIGC pricing UI.

Source: https://anyaigc.ai/pricing?provider=Doubao
Raw source: https://anyaigc.ai/api/pricing_new
Verified: 2026-11-10 (Asia/Shanghai)
Units: USD per 1 million tokens. Price strings preserve rendered UI precision.

Lowest enabled route: Doubao-2 (1.0125), below Doubao-3 (1.485).
Doubao-1 is not enabled for these models and must not be used. These route
names are research provenance only and must not appear on topic pages.

Tier boundaries and input/output prices were read from the Pro, Lite and Mini
detail dialogs and matched to each model's identical raw step definitions.
Card prices may display different trailing precision. Cached-input prices
are only shown on cards; higher-tier prices are unknown, not free. Audio is
listed separately on cards with no published tier mapping, so audio_base is
separate from rates. Context/output limits are included only where explicit
in the model descriptions. All 16 models expose POST /v1/chat/completions.
"""

MODELS = {'doubao-seed-2-1-pro-260915': {'name': 'doubao-seed-2-1-pro',
                                'rates': [{'range_zh': '模型广场显示价',
                                           'range_en': 'Listed model pricing',
                                           'input': '0.9113',
                                           'output': '4.5560',
                                           'cache': '0.1823',
                                           'audio': None}],
                                'tags': ['对话', '工具', '识图', '思考'],
                                'context': None,
                                'max_output': None,
                                'endpoint': '/v1/chat/completions',
                                'card_prices': {'input': '0.9113',
                                                'output': '4.5560',
                                                'cache': '0.1823',
                                                'audio': None},
                                'description_source': '增强 Agent '
                                                      '执行能力与多模态理解。模型能够持续推进复杂任务、协同并验收异步子任务，将图片、视频和页面理解用于推理判断与实际操作，让深度调研、办公协作和长程任务的交付更稳健。'},
 'doubao-seed-2-1-turbo-260628': {'name': 'doubao-seed-2-1-turbo',
                                  'rates': [{'range_zh': '模型广场显示价',
                                             'range_en': 'Listed model pricing',
                                             'input': '0.4556',
                                             'output': '2.2780',
                                             'cache': '0.0911',
                                             'audio': None}],
                                  'tags': ['对话', '工具', '识图', '思考'],
                                  'context': None,
                                  'max_output': None,
                                  'endpoint': '/v1/chat/completions',
                                  'card_prices': {'input': '0.4556',
                                                  'output': '2.2780',
                                                  'cache': '0.0911',
                                                  'audio': None},
                                  'description_source': 'Doubao-Seed-2.1 是面向 Coding 和 Agent '
                                                        '时代打造的新一代大模型，提供 Pro 和 Turbo '
                                                        '两个版本，分别面向高复杂度任务探索和规模化生产场景，Seed 2.1 在 '
                                                        'Coding 工程交付、Agent '
                                                        '长链路任务执行和多模态理解三大方向上全面升级，以更强的自主规划与动态修复能力，胜任真实研发与高价值生产任务。'},
 'doubao-seed-2-1-pro-260628': {'name': 'doubao-seed-2-1-pro',
                                'rates': [{'range_zh': '模型广场显示价',
                                           'range_en': 'Listed model pricing',
                                           'input': '0.9113',
                                           'output': '4.5560',
                                           'cache': '0.1823',
                                           'audio': None}],
                                'tags': ['对话', '工具', '识图', '思考'],
                                'context': None,
                                'max_output': None,
                                'endpoint': '/v1/chat/completions',
                                'card_prices': {'input': '0.9113',
                                                'output': '4.5560',
                                                'cache': '0.1823',
                                                'audio': None},
                                'description_source': '迈向生产级智能的新一代大模型，全面升级 Coding、Agent '
                                                      '与多模态能力，以更强的自主规划、长链路执行和动态修复能力，胜任企业真实复杂任务。'},
 'doubao-seed-2-0-pro-260215': {'name': 'doubao-seed-2-0-pro',
                                'rates': [{'range_zh': '输入 tokens [0, 32,000]',
                                           'range_en': 'Input tokens [0, 32,000]',
                                           'input': '0.4860',
                                           'output': '2.430',
                                           'cache': '0.0972',
                                           'audio': None},
                                          {'range_zh': '输入 tokens (32,000, 128,000]',
                                           'range_en': 'Input tokens (32,000, 128,000]',
                                           'input': '0.7290',
                                           'output': '3.645',
                                           'cache': None,
                                           'audio': None,
                                           'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                           'missing_en': 'The pricing page does not separately '
                                                         'list cached-input pricing for this '
                                                         'range.'},
                                          {'range_zh': '输入 tokens (128,000, 256,000]',
                                           'range_en': 'Input tokens (128,000, 256,000]',
                                           'input': '1.458',
                                           'output': '7.290',
                                           'cache': None,
                                           'audio': None,
                                           'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                           'missing_en': 'The pricing page does not separately '
                                                         'list cached-input pricing for this '
                                                         'range.'}],
                                'tags': ['对话', '工具'],
                                'context': None,
                                'max_output': None,
                                'endpoint': '/v1/chat/completions',
                                'card_prices': {'input': '0.4860',
                                                'output': '2.4300',
                                                'cache': '0.0972',
                                                'audio': None},
                                'description_source': 'Doubao-Seed-2.0-pro is a flagship '
                                                      'all-purpose general model designed for the '
                                                      'Agent era, tackling complex reasoning and '
                                                      'long-horizon task execution. It emphasizes '
                                                      'multimodal understanding, long-context '
                                                      'reasoning, structured generation, and '
                                                      'tool-augmented execution. Excels at complex '
                                                      'instruction following and multi-constraint '
                                                      'tasks, reliably handling multi-step '
                                                      'planning, complex vision-language '
                                                      'reasoning, video content understanding, and '
                                                      'demanding analytical workloads.'},
 'doubao-seed-2-0-lite-260215': {'name': 'doubao-seed-2-0-lite',
                                 'rates': [{'range_zh': '输入 tokens [0, 32,000]',
                                            'range_en': 'Input tokens [0, 32,000]',
                                            'input': '0.0911',
                                            'output': '0.5569',
                                            'cache': '0.0182',
                                            'audio': None},
                                           {'range_zh': '输入 tokens (32,000, 128,000]',
                                            'range_en': 'Input tokens (32,000, 128,000]',
                                            'input': '0.1367',
                                            'output': '0.8353',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'},
                                           {'range_zh': '输入 tokens (128,000, 256,000]',
                                            'range_en': 'Input tokens (128,000, 256,000]',
                                            'input': '0.2734',
                                            'output': '1.671',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'}],
                                 'tags': ['对话', '识图'],
                                 'context': None,
                                 'max_output': None,
                                 'endpoint': '/v1/chat/completions',
                                 'card_prices': {'input': '0.0911',
                                                 'output': '0.5569',
                                                 'cache': '0.0182',
                                                 'audio': '0.6701'},
                                 'description_source': 'Doubao-Seed-2.0-lite is a balanced model '
                                                       'for high-frequency enterprise scenarios, '
                                                       'trading performance against cost. It '
                                                       'surpasses the previous-generation '
                                                       'Doubao-Seed-1.8 in overall capability, '
                                                       'handling unstructured information '
                                                       'processing, content creation, search and '
                                                       'recommendation, and data analysis. '
                                                       'Supports long context, multi-source '
                                                       'information fusion, multi-step instruction '
                                                       'execution, and high-fidelity structured '
                                                       'output — delivering consistent results at '
                                                       'significantly reduced cost.',
                                 'audio_base': '0.6701',
                                 'audio_scope_zh': '模型广场单列的音频输入基础显示价；页面未公开它与输入 tokens 阶梯的对应关系。',
                                 'audio_scope_en': 'The separately listed base audio-input price; '
                                                   'the page does not publish how it maps to '
                                                   'input-token tiers.'},
 'doubao-seed-2-0-lite-260428': {'name': 'doubao-seed-2-0-lite',
                                 'rates': [{'range_zh': '输入 tokens [0, 32,000]',
                                            'range_en': 'Input tokens [0, 32,000]',
                                            'input': '0.0911',
                                            'output': '0.5569',
                                            'cache': '0.0182',
                                            'audio': None},
                                           {'range_zh': '输入 tokens (32,000, 128,000]',
                                            'range_en': 'Input tokens (32,000, 128,000]',
                                            'input': '0.1367',
                                            'output': '0.8353',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'},
                                           {'range_zh': '输入 tokens (128,000, 256,000]',
                                            'range_en': 'Input tokens (128,000, 256,000]',
                                            'input': '0.2734',
                                            'output': '1.671',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'}],
                                 'tags': ['对话', '工具'],
                                 'context': None,
                                 'max_output': None,
                                 'endpoint': '/v1/chat/completions',
                                 'card_prices': {'input': '0.0911',
                                                 'output': '0.5569',
                                                 'cache': '0.0182',
                                                 'audio': '0.6701'},
                                 'description_source': 'The first omnimodal understanding model in '
                                                       'the Doubao family, supporting native '
                                                       'unified understanding of video, images, '
                                                       'audio, and text, with upgraded Agent, '
                                                       'Coding, and GUI capabilities.',
                                 'audio_base': '0.6701',
                                 'audio_scope_zh': '模型广场单列的音频输入基础显示价；页面未公开它与输入 tokens 阶梯的对应关系。',
                                 'audio_scope_en': 'The separately listed base audio-input price; '
                                                   'the page does not publish how it maps to '
                                                   'input-token tiers.'},
 'doubao-seed-1-8-251228': {'name': 'doubao-seed-1-8',
                            'rates': [{'range_zh': '模型广场显示价',
                                       'range_en': 'Listed model pricing',
                                       'input': '0.1215',
                                       'output': '1.2150',
                                       'cache': None,
                                       'audio': None}],
                            'tags': ['对话', '识图', '工具'],
                            'context': None,
                            'max_output': None,
                            'endpoint': '/v1/chat/completions',
                            'card_prices': {'input': '0.1215',
                                            'output': '1.2150',
                                            'cache': None,
                                            'audio': None},
                            'description_source': 'doubao-seed-1.8 delivers stronger multimodal '
                                                  'understanding and Agent capabilities, achieving '
                                                  'outstanding performance across many complex '
                                                  'real-world tasks and further helping '
                                                  'enterprises create value.'},
 'doubao-seed-2-0-mini-260428': {'name': 'doubao-seed-2-0-mini',
                                 'rates': [{'range_zh': '输入 tokens [0, 32,000]',
                                            'range_en': 'Input tokens [0, 32,000]',
                                            'input': '0.0304',
                                            'output': '0.3038',
                                            'cache': '0.0061',
                                            'audio': None},
                                           {'range_zh': '输入 tokens (32,000, 128,000]',
                                            'range_en': 'Input tokens (32,000, 128,000]',
                                            'input': '0.0608',
                                            'output': '0.6075',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'},
                                           {'range_zh': '输入 tokens (128,000, 256,000]',
                                            'range_en': 'Input tokens (128,000, 256,000]',
                                            'input': '0.1215',
                                            'output': '1.215',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'}],
                                 'tags': ['对话', '工具'],
                                 'context': None,
                                 'max_output': None,
                                 'endpoint': '/v1/chat/completions',
                                 'card_prices': {'input': '0.0304',
                                                 'output': '0.3038',
                                                 'cache': '0.0061',
                                                 'audio': '0.2234'},
                                 'description_source': 'An omnimodal understanding model in the '
                                                       'Doubao family with shorter thinking length '
                                                       'and higher token efficiency.',
                                 'audio_base': '0.2234',
                                 'audio_scope_zh': '模型广场单列的音频输入基础显示价；页面未公开它与输入 tokens 阶梯的对应关系。',
                                 'audio_scope_en': 'The separately listed base audio-input price; '
                                                   'the page does not publish how it maps to '
                                                   'input-token tiers.'},
 'doubao-seed-2-0-code-preview-260215': {'name': 'doubao-seed-2-0-code-preview',
                                         'rates': [{'range_zh': '输入 tokens [0, 32,000]',
                                                    'range_en': 'Input tokens [0, 32,000]',
                                                    'input': '0.4860',
                                                    'output': '2.430',
                                                    'cache': '0.0972',
                                                    'audio': None},
                                                   {'range_zh': '输入 tokens (32,000, 128,000]',
                                                    'range_en': 'Input tokens (32,000, 128,000]',
                                                    'input': '0.7290',
                                                    'output': '3.645',
                                                    'cache': None,
                                                    'audio': None,
                                                    'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                                    'missing_en': 'The pricing page does not '
                                                                  'separately list cached-input '
                                                                  'pricing for this range.'},
                                                   {'range_zh': '输入 tokens (128,000, 256,000]',
                                                    'range_en': 'Input tokens (128,000, 256,000]',
                                                    'input': '1.458',
                                                    'output': '7.290',
                                                    'cache': None,
                                                    'audio': None,
                                                    'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                                    'missing_en': 'The pricing page does not '
                                                                  'separately list cached-input '
                                                                  'pricing for this range.'}],
                                         'tags': ['对话', '思考', '识图'],
                                         'context': None,
                                         'max_output': None,
                                         'endpoint': '/v1/chat/completions',
                                         'card_prices': {'input': '0.4860',
                                                         'output': '2.4300',
                                                         'cache': '0.0972',
                                                         'audio': None},
                                         'description_source': 'Doubao-Seed-2.0-Code is optimized '
                                                               'for enterprise-level programming '
                                                               "needs. Building on Seed 2.0's "
                                                               'strong Agent and VLM capabilities, '
                                                               'it significantly enhances code '
                                                               'generation — excelling at frontend '
                                                               'development while offering '
                                                               'specialized optimization for the '
                                                               'multi-language coding scenarios '
                                                               'common in enterprise environments. '
                                                               'Ideal for integration with AI '
                                                               'programming tools.'},
 'doubao-seed-2-0-mini-260215': {'name': 'doubao-seed-2-0-mini',
                                 'rates': [{'range_zh': '输入 tokens [0, 32,000]',
                                            'range_en': 'Input tokens [0, 32,000]',
                                            'input': '0.0304',
                                            'output': '0.3038',
                                            'cache': '0.0061',
                                            'audio': None},
                                           {'range_zh': '输入 tokens (32,000, 128,000]',
                                            'range_en': 'Input tokens (32,000, 128,000]',
                                            'input': '0.0608',
                                            'output': '0.6075',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'},
                                           {'range_zh': '输入 tokens (128,000, 256,000]',
                                            'range_en': 'Input tokens (128,000, 256,000]',
                                            'input': '0.1215',
                                            'output': '1.215',
                                            'cache': None,
                                            'audio': None,
                                            'missing_zh': '模型广场未单列此区间的缓存命中单价。',
                                            'missing_en': 'The pricing page does not separately '
                                                          'list cached-input pricing for this '
                                                          'range.'}],
                                 'tags': ['对话', '识图'],
                                 'context': '256K',
                                 'max_output': None,
                                 'endpoint': '/v1/chat/completions',
                                 'card_prices': {'input': '0.0304',
                                                 'output': '0.3038',
                                                 'cache': '0.0061',
                                                 'audio': '0.2234'},
                                 'description_source': 'Doubao-Seed-2.0-mini targets low-latency, '
                                                       'high-concurrency, and cost-sensitive '
                                                       'scenarios, delivering maximum inference '
                                                       'speed. Performance is on par with '
                                                       'Doubao-Seed-1.6. Supports 256K context, '
                                                       'four thinking-depth levels, and multimodal '
                                                       'understanding — ideal for lightweight '
                                                       'tasks where speed and cost are the '
                                                       'priority.',
                                 'audio_base': '0.2234',
                                 'audio_scope_zh': '模型广场单列的音频输入基础显示价；页面未公开它与输入 tokens 阶梯的对应关系。',
                                 'audio_scope_en': 'The separately listed base audio-input price; '
                                                   'the page does not publish how it maps to '
                                                   'input-token tiers.'},
 'doubao-seed-1-6-250615': {'name': 'doubao-seed-1-6',
                            'rates': [{'range_zh': '模型广场显示价',
                                       'range_en': 'Listed model pricing',
                                       'input': '0.1215',
                                       'output': '1.2150',
                                       'cache': None,
                                       'audio': None}],
                            'tags': ['对话', '思考', '多模态'],
                            'context': '256K',
                            'max_output': None,
                            'endpoint': '/v1/chat/completions',
                            'card_prices': {'input': '0.1215',
                                            'output': '1.2150',
                                            'cache': None,
                                            'audio': None},
                            'description_source': 'A versatile all-around model and the first in '
                                                  'China to support 256K context with thinking '
                                                  'capability. Features deep thinking, multimodal '
                                                  'understanding, and GUI operation. Users can '
                                                  'flexibly enable or disable deep thinking as '
                                                  'needed; adaptive thinking mode automatically '
                                                  'determines whether to activate deep thinking '
                                                  'based on prompt complexity, improving output '
                                                  'quality while significantly reducing token '
                                                  'consumption.'},
 'doubao-seed-1-6-251015': {'name': 'doubao-seed-1-6',
                            'rates': [{'range_zh': '模型广场显示价',
                                       'range_en': 'Listed model pricing',
                                       'input': '0.1215',
                                       'output': '1.2150',
                                       'cache': None,
                                       'audio': None}],
                            'tags': ['对话', '识图', '思考'],
                            'context': None,
                            'max_output': None,
                            'endpoint': '/v1/chat/completions',
                            'card_prices': {'input': '0.1215',
                                            'output': '1.2150',
                                            'cache': None,
                                            'audio': None},
                            'description_source': 'Supports adjustable thinking depth via the '
                                                  'reasoning_effort field in the API, with four '
                                                  'modes: minimal, low, medium, and high. This '
                                                  'compresses overall output length to balance '
                                                  'quality, latency, and cost across different use '
                                                  'cases.'},
 'doubao-seed-1-6-flash-250828': {'name': 'doubao-seed-1-6-flash',
                                  'rates': [{'range_zh': '模型广场显示价',
                                             'range_en': 'Listed model pricing',
                                             'input': '0.0456',
                                             'output': '0.4556',
                                             'cache': None,
                                             'audio': None}],
                                  'tags': ['对话', '思考', '多模态'],
                                  'context': '256K',
                                  'max_output': None,
                                  'endpoint': '/v1/chat/completions',
                                  'card_prices': {'input': '0.0456',
                                                  'output': '0.4556',
                                                  'cache': None,
                                                  'audio': None},
                                  'description_source': 'Ultra-fast response variant in the Doubao '
                                                        '1.6 series. Features deep thinking and '
                                                        'multimodal understanding with 256K '
                                                        'context support. Extremely low latency — '
                                                        'TOPT (Top-of-Pipeline Time) as low as 10 '
                                                        'ms — for near-instant responses. Visual '
                                                        'understanding performance is on par with '
                                                        'flagship models from other leading '
                                                        'vendors. Ideal for latency-sensitive '
                                                        'scenarios such as real-time interaction '
                                                        'and vision task processing.'},
 'doubao-seed-1-6-thinking-250615': {'name': 'doubao-seed-1-6-thinking',
                                     'rates': [{'range_zh': '模型广场显示价',
                                                'range_en': 'Listed model pricing',
                                                'input': '0.1215',
                                                'output': '1.2150',
                                                'cache': None,
                                                'audio': None}],
                                     'tags': ['对话', '思考', '多模态'],
                                     'context': '256K',
                                     'max_output': None,
                                     'endpoint': '/v1/chat/completions',
                                     'card_prices': {'input': '0.1215',
                                                     'output': '1.2150',
                                                     'cache': None,
                                                     'audio': None},
                                     'description_source': 'The enhanced deep-thinking variant of '
                                                           'the Doubao 1.6 series, focused on deep '
                                                           'reasoning. Further improves coding, '
                                                           'math, and logical reasoning to handle '
                                                           'more complex tasks. Supports 256K '
                                                           'context for understanding and '
                                                           'generating longer content, ideal for '
                                                           'in-depth analysis and complex '
                                                           'reasoning scenarios.'},
 'doubao-seed-1-6-thinking-250715': {'name': 'doubao-seed-1-6-thinking',
                                     'rates': [{'range_zh': '模型广场显示价',
                                                'range_en': 'Listed model pricing',
                                                'input': '0.1215',
                                                'output': '1.2150',
                                                'cache': None,
                                                'audio': None}],
                                     'tags': ['对话', '多模态'],
                                     'context': None,
                                     'max_output': None,
                                     'endpoint': '/v1/chat/completions',
                                     'card_prices': {'input': '0.1215',
                                                     'output': '1.2150',
                                                     'cache': None,
                                                     'audio': None},
                                     'description_source': 'Significantly enhanced thinking '
                                                           'capability. Compared to the Doubao '
                                                           '1.5-generation deep-understanding '
                                                           'model, it further improves core skills '
                                                           'in coding, math, and logical '
                                                           'reasoning, and adds visual '
                                                           'understanding support.'},
 'doubao-seed-1-6-vision-250815': {'name': 'doubao-seed-1-6-vision',
                                   'rates': [{'range_zh': '模型广场显示价',
                                              'range_en': 'Listed model pricing',
                                              'input': '0.2430',
                                              'output': '1.9440',
                                              'cache': None,
                                              'audio': None}],
                                   'tags': ['对话', '多模态', '识图'],
                                   'context': '256K',
                                   'max_output': '64K',
                                   'endpoint': '/v1/chat/completions',
                                   'card_prices': {'input': '0.2430',
                                                   'output': '1.9440',
                                                   'cache': None,
                                                   'audio': None},
                                   'description_source': 'Doubao-Seed-1.6-vision is a vision '
                                                         'deep-thinking model with stronger '
                                                         'general multimodal understanding and '
                                                         'reasoning for education, image review, '
                                                         'inspection and security, and AI search '
                                                         'Q&A scenarios. Supports a 256K context '
                                                         'window with a maximum output length of '
                                                         '64K tokens.'}}

SLUGS = list(MODELS)
