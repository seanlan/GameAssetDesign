import React from 'react';

const translations = {
  en: {
    // Top bar
    'app.title': 'Game Asset Manager',
    'app.upload': 'Upload',
    'app.generate': 'Generate',
    'app.refresh': 'Refresh',

    // Filter bar
    'filter.all': 'All',
    'filter.character': 'Character',
    'filter.icon': 'Icon',
    'filter.ui': 'UI',
    'filter.card': 'Card',
    'filter.background': 'Background',
    'filter.sprite': 'Sprite',
    'filter.tileset': 'Tileset',
    'filter.search': 'Search assets...',
    'filter.byTime': 'By Time',
    'filter.byType': 'By Type',
    'filter.byName': 'By Name',
    'filter.assets': 'assets',
    'filter.selectAll': 'Select All',
    'filter.deselect': 'Deselect',
    'filter.tagFilter': 'Filter by tag...',

    // Asset card
    'card.shared': 'shared',

    // Detail panel
    'detail.close': 'Close',
    'detail.type': 'Type',
    'detail.size': 'Size',
    'detail.fileSize': 'File Size',
    'detail.model': 'Model',
    'detail.style': 'Style',
    'detail.time': 'Time',
    'detail.prompt': 'Prompt',
    'detail.noPrompt': 'No prompt recorded',
    'detail.relationships': 'Relationships',
    'detail.noRelationships': 'None',
    'detail.versions': 'Version History',
    'detail.noVersions': 'No version history',
    'detail.loading': 'Loading...',
    'detail.rollback': 'Rollback',
    'detail.compare': 'Compare',
    'detail.tags': 'Tags',
    'detail.addTag': 'Add tag...',

    // Action panel
    'action.selected': 'Selected',
    'action.assets': 'assets',
    'action.refine': 'Refine',
    'action.type': 'Type',
    'action.note': 'Describe what to change...',
    'action.submit': 'Submit',
    'action.delete': 'Delete',
    'action.export': 'Export',
    'action.atlas': 'Atlas',
    'action.working': 'Working...',

    // Upload panel
    'upload.title': 'Upload Design Image',
    'upload.dragDrop': 'Drag & drop design image here',
    'upload.or': 'or',
    'upload.browse': 'Browse Files',
    'upload.quickExtract': '⚡ Quick Extract',
    'upload.analyze': 'Analyze',
    'upload.analyzing': 'Analyzing...',
    'upload.extract': 'Extract Assets',
    'upload.extracting': 'Extracting...',
    'upload.processing': 'Processing...',
    'upload.detected': 'Detected Elements',
    'upload.visual': 'Visual',
    'upload.numeric': 'Numeric',
    'upload.save': 'Save & Re-annotate',
    'upload.saving': 'Saving...',
    'upload.layer': 'Layer',
    'upload.addElement': 'Add Element to',

    // Generate panel
    'generate.title': 'Generate Asset',
    'generate.description': 'Describe the asset...',
    'generate.type': 'Asset Type',
    'generate.style': 'Style (optional)',
    'generate.none': 'None (use project default)',
    'generate.submit': 'Generate',
    'generate.generating': 'Generating...',

    // Stats
    'stats.total': 'Total',
    'stats.storage': 'Storage',

    // Compare
    'compare.title': 'Before / After',

    // API Key
    'apikey.title': 'Gemini API Key Required',
    'apikey.description': 'Set the GEMINI_API_KEY environment variable before starting the server:',
    'apikey.dismiss': 'Got it',

    // Empty/Loading states
    'empty.noAssets': 'No assets found',
    'loading.assets': 'Loading assets...',

    // Progress
    'progress.characters': 'Characters',
    'progress.icons': 'Icons',
    'progress.ui': 'UI',
    'progress.cards': 'Cards',
    'progress.backgrounds': 'Backgrounds',
    'progress.sprites': 'Sprites',
    'progress.tilesets': 'Tilesets',
  },
  zh: {
    'app.title': '游戏素材管理器',
    'app.upload': '上传',
    'app.generate': '生成',
    'app.refresh': '刷新',

    'filter.all': '全部',
    'filter.character': '角色',
    'filter.icon': '图标',
    'filter.ui': 'UI',
    'filter.card': '卡牌',
    'filter.background': '背景',
    'filter.sprite': '精灵图',
    'filter.tileset': '瓦片',
    'filter.search': '搜索素材...',
    'filter.byTime': '按时间',
    'filter.byType': '按类型',
    'filter.byName': '按名称',
    'filter.assets': '个素材',
    'filter.selectAll': '全选',
    'filter.deselect': '取消',
    'filter.tagFilter': '按标签筛选...',

    'card.shared': '共享',

    'detail.close': '关闭',
    'detail.type': '类型',
    'detail.size': '尺寸',
    'detail.fileSize': '文件大小',
    'detail.model': '模型',
    'detail.style': '风格',
    'detail.time': '时间',
    'detail.prompt': '提示词',
    'detail.noPrompt': '无提示词记录',
    'detail.relationships': '关联',
    'detail.noRelationships': '无',
    'detail.versions': '版本历史',
    'detail.noVersions': '无版本历史',
    'detail.loading': '加载中...',
    'detail.rollback': '回滚',
    'detail.compare': '对比',
    'detail.tags': '标签',
    'detail.addTag': '添加标签...',

    'action.selected': '已选择',
    'action.assets': '个素材',
    'action.refine': '精修',
    'action.type': '类型',
    'action.note': '描述需要修改的内容...',
    'action.submit': '提交',
    'action.delete': '删除',
    'action.export': '导出',
    'action.atlas': '图集',
    'action.working': '处理中...',

    'upload.title': '上传设计图',
    'upload.dragDrop': '拖拽设计图到此处',
    'upload.or': '或',
    'upload.browse': '选择文件',
    'upload.quickExtract': '⚡ 一键提取',
    'upload.analyze': '分析',
    'upload.analyzing': '分析中...',
    'upload.extract': '提取素材',
    'upload.extracting': '提取中...',
    'upload.processing': '处理中...',
    'upload.detected': '检测到的元素',
    'upload.visual': '可视化',
    'upload.numeric': '数值',
    'upload.save': '保存并重新标注',
    'upload.saving': '保存中...',
    'upload.layer': '层级',
    'upload.addElement': '添加元素到',

    'generate.title': '生成素材',
    'generate.description': '描述素材...',
    'generate.type': '素材类型',
    'generate.style': '风格（可选）',
    'generate.none': '无（使用项目默认）',
    'generate.submit': '生成',
    'generate.generating': '生成中...',

    'stats.total': '总计',
    'stats.storage': '存储',

    'compare.title': '修改前 / 修改后',

    'apikey.title': '需要 Gemini API Key',
    'apikey.description': '启动服务前设置 GEMINI_API_KEY 环境变量：',
    'apikey.dismiss': '知道了',

    'empty.noAssets': '暂无素材',
    'loading.assets': '加载中...',

    'progress.characters': '角色',
    'progress.icons': '图标',
    'progress.ui': 'UI',
    'progress.cards': '卡牌',
    'progress.backgrounds': '背景',
    'progress.sprites': '精灵图',
    'progress.tilesets': '瓦片',
  },
};

type Lang = 'en' | 'zh';

function detectLanguage(): Lang {
  const saved = localStorage.getItem('game-asset-lang');
  if (saved === 'en' || saved === 'zh') return saved;
  const browserLang = navigator.language.toLowerCase();
  return browserLang.startsWith('zh') ? 'zh' : 'en';
}

let currentLang: Lang = detectLanguage();
const listeners: Set<() => void> = new Set();

export function getLang(): Lang {
  return currentLang;
}

export function setLang(lang: Lang): void {
  currentLang = lang;
  localStorage.setItem('game-asset-lang', lang);
  listeners.forEach((fn) => fn());
}

export function t(key: string): string {
  const dict = translations[currentLang];
  return (dict as Record<string, string>)[key] ?? key;
}

export function useLang(): [Lang, (lang: Lang) => void] {
  const [, forceUpdate] = React.useState(0);
  React.useEffect(() => {
    const update = () => forceUpdate((n) => n + 1);
    listeners.add(update);
    return () => {
      listeners.delete(update);
    };
  }, []);
  return [currentLang, setLang];
}
