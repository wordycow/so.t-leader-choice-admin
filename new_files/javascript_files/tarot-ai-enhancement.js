// 🔮 타로 AI 고도화 시스템 - 딥 러닝 기반 해석

const TAROT_AI_ENGINE = {
  // AI 기반 카드 조합 분석
  analyzeCardCombination: function(cards) {
    const energyMap = {
      major: { weight: 3, influence: 'universal' },
      cups: { weight: 2, influence: 'emotional' },
      swords: { weight: 2, influence: 'mental' },
      pentacles: { weight: 2, influence: 'material' },
      wands: { weight: 2, influence: 'creative' }
    };
    
    let dominantEnergy = '';
    let energyScore = {};
    
    cards.forEach(card => {
      const suit = this.detectSuit(card.id);
      energyScore[suit] = (energyScore[suit] || 0) + energyMap[suit].weight;
    });
    
    dominantEnergy = Object.keys(energyScore).reduce((a, b) => 
      energyScore[a] > energyScore[b] ? a : b
    );
    
    return {
      dominantEnergy,
      energyScore,
      synthesisLevel: this.calculateSynthesis(cards)
    };
  },
  
  detectSuit: function(cardId) {
    if (cardId <= 21) return 'major';
    if (cardId >= 22 && cardId <= 35) return 'cups';
    if (cardId >= 36 && cardId <= 49) return 'swords';
    if (cardId >= 50 && cardId <= 63) return 'pentacles';
    return 'wands';
  },
  
  calculateSynthesis: function(cards) {
    const uprightCount = cards.filter(c => !c.reversed).length;
    const ratio = uprightCount / cards.length;
    
    if (ratio >= 0.8) return 'highly_positive';
    if (ratio >= 0.6) return 'positive';
    if (ratio >= 0.4) return 'balanced';
    if (ratio >= 0.2) return 'challenging';
    return 'transformative';
  },
  
  // 시간대별 에너지 분석 (3장 스프레드)
  analyzeTimeline: function(cards) {
    if (cards.length !== 3) return null;
    
    return {
      past: {
        card: cards[0],
        influence: this.getInfluenceLevel(cards[0]),
        lesson: this.extractLesson(cards[0])
      },
      present: {
        card: cards[1],
        challenge: this.getChallenge(cards[1]),
        opportunity: this.getOpportunity(cards[1])
      },
      future: {
        card: cards[2],
        potential: this.getPotential(cards[2]),
        advice: this.getAdvice(cards[2])
      },
      overallFlow: this.analyzeFlow(cards)
    };
  },
  
  getInfluenceLevel: function(card) {
    const intensity = {
      0: 'transformative', 8: 'powerful', 13: 'profound',
      16: 'shocking', 19: 'brilliant', 21: 'complete'
    };
    return intensity[card.id] || 'moderate';
  },
  
  extractLesson: function(card) {
    return card.reversed ? 
      '과거의 저항을 극복하고 앞으로 나아갈 때입니다' : 
      '과거의 경험이 현재의 지혜가 되었습니다';
  },
  
  getChallenge: function(card) {
    const suit = this.detectSuit(card.id);
    const challenges = {
      major: '인생의 중대한 전환점',
      cups: '감정적 균형 찾기',
      swords: '명료한 사고와 결단',
      pentacles: '물질적 안정 구축',
      wands: '창조적 에너지 관리'
    };
    return challenges[suit];
  },
  
  getOpportunity: function(card) {
    return card.reversed ?
      '숨겨진 가능성을 발견할 기회' :
      '명확한 방향으로 나아갈 기회';
  },
  
  getPotential: function(card) {
    const suit = this.detectSuit(card.id);
    const potentials = {
      major: '운명적 성취',
      cups: '깊은 감정적 만족',
      swords: '지적 명료함과 승리',
      pentacles: '물질적 풍요와 안정',
      wands: '창조적 혁신'
    };
    return potentials[suit];
  },
  
  getAdvice: function(card) {
    return card.reversed ?
      '내면을 돌아보고 재정비하세요' :
      '자신감을 가지고 전진하세요';
  },
  
  analyzeFlow: function(cards) {
    const energy = cards.map(c => c.reversed ? -1 : 1);
    const sum = energy.reduce((a, b) => a + b, 0);
    
    if (sum === 3) return '상승 에너지 - 긍정적 발전';
    if (sum === -3) return '전환 에너지 - 재구성 시기';
    if (energy[0] < 0 && energy[2] > 0) return '회복 에너지 - 어려움 극복';
    if (energy[0] > 0 && energy[2] < 0) return '경계 에너지 - 신중함 필요';
    return '균형 에너지 - 조화로운 발전';
  },
  
  // 종합 AI 해석 생성
  generateAIReading: function(cards, spread) {
    const combination = this.analyzeCardCombination(cards);
    const timeline = spread === 'three' ? this.analyzeTimeline(cards) : null;
    
    return {
      combination,
      timeline,
      deepInsight: this.generateDeepInsight(cards, combination),
      actionSteps: this.generateActionSteps(cards, combination),
      affirmation: this.generateAffirmation(combination)
    };
  },
  
  generateDeepInsight: function(cards, combination) {
    const insights = {
      highly_positive: '현재 당신의 에너지는 완벽한 조화를 이루고 있습니다. 우주가 당신을 지지하고 있으며, 원하는 것을 현실화할 최적의 시기입니다.',
      positive: '긍정적인 흐름이 당신을 감싸고 있습니다. 약간의 노력으로 큰 성과를 얻을 수 있는 시기입니다.',
      balanced: '균형 잡힌 에너지 속에서 당신은 선택의 기로에 있습니다. 내면의 목소리에 귀 기울이세요.',
      challenging: '도전적인 시기이지만, 이는 성장의 기회입니다. 어려움을 통해 더 강해질 것입니다.',
      transformative: '심오한 변화의 시기입니다. 과거를 놓아주고 새로운 자아로 다시 태어나세요.'
    };
    return insights[combination.synthesisLevel];
  },
  
  generateActionSteps: function(cards, combination) {
    const steps = [];
    
    if (combination.dominantEnergy === 'emotional') {
      steps.push('💙 감정 일기를 작성하며 내면을 탐색하세요');
      steps.push('🤝 소중한 사람들과 깊은 대화를 나누세요');
    }
    if (combination.dominantEnergy === 'mental') {
      steps.push('🧠 명상이나 심호흡으로 마음을 정리하세요');
      steps.push('📝 생각을 글로 정리하고 계획을 세우세요');
    }
    if (combination.dominantEnergy === 'material') {
      steps.push('💰 재정 계획을 점검하고 실행하세요');
      steps.push('🎯 구체적이고 실현 가능한 목표를 설정하세요');
    }
    if (combination.dominantEnergy === 'creative') {
      steps.push('🎨 창의적 활동에 시간을 투자하세요');
      steps.push('🚀 새로운 프로젝트를 시작할 용기를 내세요');
    }
    
    return steps;
  },
  
  generateAffirmation: function(combination) {
    const affirmations = {
      highly_positive: '나는 우주의 완벽한 타이밍을 신뢰합니다. 모든 것이 최선으로 흘러갑니다.',
      positive: '나는 긍정적 에너지를 끌어당기며, 나의 꿈을 현실로 만듭니다.',
      balanced: '나는 균형과 조화 속에서 지혜로운 선택을 합니다.',
      challenging: '나는 모든 도전을 성장의 기회로 받아들입니다. 나는 강합니다.',
      transformative: '나는 변화를 두려워하지 않습니다. 나는 계속 진화하고 있습니다.'
    };
    return affirmations[combination.synthesisLevel];
  }
};

// Export for use in tarot.html
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TAROT_AI_ENGINE;
}
