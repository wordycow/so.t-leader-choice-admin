// 🎴 사주 AI 고도화 시스템 - 오행 균형 분석

const SAJU_AI_ENGINE = {
  // 오행 균형 분석
  analyzeBalance: function(elements) {
    const total = Object.values(elements).reduce((a, b) => a + b, 0);
    const balance = {};
    
    for (let [elem, count] of Object.entries(elements)) {
      balance[elem] = {
        count,
        percentage: ((count / total) * 100).toFixed(1),
        strength: this.getStrength(count, total)
      };
    }
    
    return {
      balance,
      dominant: this.findDominant(elements),
      lacking: this.findLacking(elements),
      harmony: this.calculateHarmony(elements)
    };
  },
  
  getStrength: function(count, total) {
    const ratio = count / total;
    if (ratio >= 0.35) return '매우 강함';
    if (ratio >= 0.25) return '강함';
    if (ratio >= 0.15) return '보통';
    if (ratio >= 0.08) return '약함';
    return '매우 약함';
  },
  
  findDominant: function(elements) {
    const sorted = Object.entries(elements).sort((a, b) => b[1] - a[1]);
    return {
      element: sorted[0][0],
      count: sorted[0][1]
    };
  },
  
  findLacking: function(elements) {
    const sorted = Object.entries(elements).sort((a, b) => a[1] - b[1]);
    return {
      element: sorted[0][0],
      count: sorted[0][1]
    };
  },
  
  calculateHarmony: function(elements) {
    const counts = Object.values(elements);
    const avg = counts.reduce((a, b) => a + b, 0) / counts.length;
    const variance = counts.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / counts.length;
    const std = Math.sqrt(variance);
    
    if (std < 1) return { level: '완벽한 조화', score: 95 };
    if (std < 2) return { level: '매우 조화로움', score: 85 };
    if (std < 3) return { level: '조화로움', score: 70 };
    if (std < 4) return { level: '불균형', score: 50 };
    return { level: '심각한 불균형', score: 30 };
  },
  
  // 오행 상생상극 분석
  analyzeInteractions: function(elements) {
    const interactions = {
      wood: { generates: 'fire', controls: 'earth', generatedBy: 'water', controlledBy: 'metal' },
      fire: { generates: 'earth', controls: 'metal', generatedBy: 'wood', controlledBy: 'water' },
      earth: { generates: 'metal', controls: 'water', generatedBy: 'fire', controlledBy: 'wood' },
      metal: { generates: 'water', controls: 'wood', generatedBy: 'earth', controlledBy: 'fire' },
      water: { generates: 'wood', controls: 'fire', generatedBy: 'metal', controlledBy: 'earth' }
    };
    
    const dominant = this.findDominant(elements).element;
    const lacking = this.findLacking(elements).element;
    
    return {
      supportive: interactions[dominant].generates,
      challenging: interactions[dominant].controlledBy,
      needsSupport: interactions[lacking].generatedBy,
      recommendation: this.generateRecommendation(dominant, lacking, interactions)
    };
  },
  
  generateRecommendation: function(dominant, lacking, interactions) {
    const elementNames = {
      wood: '목(木)', fire: '화(火)', earth: '토(土)', 
      metal: '금(金)', water: '수(水)'
    };
    
    const colors = {
      wood: '녹색, 청색',
      fire: '적색, 주황색',
      earth: '황색, 갈색',
      metal: '백색, 금색',
      water: '흑색, 남색'
    };
    
    const directions = {
      wood: '동쪽',
      fire: '남쪽',
      earth: '중앙',
      metal: '서쪽',
      water: '북쪽'
    };
    
    return {
      strengthenElement: elementNames[lacking],
      colors: colors[lacking],
      direction: directions[lacking],
      advice: `${elementNames[lacking]} 기운을 보충하기 위해 ${colors[lacking]} 계열의 옷이나 소품을 활용하고, ${directions[lacking]} 방향을 중시하세요.`
    };
  },
  
  // 종합 AI 해석 생성
  generateAIReading: function(birthData, elements, gender) {
    const balance = this.analyzeBalance(elements);
    const interactions = this.analyzeInteractions(elements);
    const dominant = this.findDominant(elements).element;
    const lacking = this.findLacking(elements).element;
    
    // 오행 이름 한글 변환
    const translateElem = (e) => {
      const names = {
        wood: '목(木)', fire: '화(火)', earth: '토(土)', 
        metal: '금(金)', water: '수(水)'
      };
      return names[e] || e;
    };
    
    // 부족/과잉 오행 찾기
    const counts = Object.values(elements);
    const avg = counts.reduce((a, b) => a + b, 0) / counts.length;
    const lackingElements = [];
    const excessiveElements = [];
    
    for (let [elem, count] of Object.entries(elements)) {
      if (count < avg * 0.5) lackingElements.push(elem);
      if (count > avg * 1.5) excessiveElements.push(elem);
    }
    
    // 보완 방법 (색상, 방향)
    const colors = {
      wood: '녹색, 청색', fire: '적색, 주황색', earth: '황색, 갈색',
      metal: '백색, 금색', water: '흑색, 남색'
    };
    const directions = {
      wood: '동쪽', fire: '남쪽', earth: '중앙', metal: '서쪽', water: '북쪽'
    };
    
    // 상생상극 관계
    const interactionRules = {
      wood: { generates: 'fire', controls: 'earth', generatedBy: 'water', controlledBy: 'metal' },
      fire: { generates: 'earth', controls: 'metal', generatedBy: 'wood', controlledBy: 'water' },
      earth: { generates: 'metal', controls: 'water', generatedBy: 'fire', controlledBy: 'wood' },
      metal: { generates: 'water', controls: 'wood', generatedBy: 'earth', controlledBy: 'fire' },
      water: { generates: 'wood', controls: 'fire', generatedBy: 'metal', controlledBy: 'earth' }
    };
    
    const supporting = [interactionRules[dominant].generatedBy, interactionRules[dominant].generates];
    const conflicting = [interactionRules[dominant].controlledBy, interactionRules[dominant].controls];
    
    // 성격, 직업, 건강, 인간관계, 재물 분석
    const personality = this.analyzePersonality(balance);
    const career = this.analyzeCareer(balance);
    const health = this.analyzeHealth(balance);
    const relationships = this.analyzeRelationships(balance);
    const fortune = this.generateFortune(balance, interactions);
    
    return {
      balance: {
        description: balance.harmony.level,
        lacking: lackingElements,
        excessive: excessiveElements
      },
      recommendation: {
        color: colors[lacking] || '다양한 색상',
        direction: directions[lacking] || '자유로운 방향'
      },
      interaction: {
        supporting: supporting,
        conflicting: conflicting,
        harmony: `${translateElem(interactionRules[dominant].generatedBy)} 기운을 보완하고 ${translateElem(interactionRules[dominant].controlledBy)} 기운과의 충돌을 피하세요`
      },
      insight: {
        personality: `${personality.core}. 강점: ${personality.positive}, 약점: ${personality.negative}`,
        career: `추천 분야: ${career.suitable}. ${career.advice}`,
        health: `주의 부위: ${health.vulnerable}. ${health.advice}`,
        relationship: `최고 궁합: ${translateElem(relationships.best)}, 좋은 궁합: ${translateElem(relationships.good)}, 피해야 할 궁합: ${translateElem(relationships.avoid)}`,
        fortune: fortune.overall
      },
      advice: this.generateLifeAdvice(balance, interactions)
    };
  },
  
  analyzePersonality: function(balance) {
    const dominant = balance.dominant.element;
    
    const traits = {
      wood: {
        positive: '창의적, 성장지향적, 유연함, 친화력',
        negative: '우유부단, 과도한 이상주의',
        core: '끊임없이 성장하고 확장하려는 에너지'
      },
      fire: {
        positive: '열정적, 리더십, 카리스마, 직관력',
        negative: '충동적, 조급함, 공격성',
        core: '타오르는 열정과 변화의 에너지'
      },
      earth: {
        positive: '안정적, 신뢰감, 포용력, 실용적',
        negative: '고집, 변화 거부, 과도한 신중함',
        core: '중심을 잡고 조화를 이루는 에너지'
      },
      metal: {
        positive: '논리적, 결단력, 정의감, 원칙주의',
        negative: '냉정함, 경직성, 완벽주의',
        core: '날카로운 분석과 정확한 판단의 에너지'
      },
      water: {
        positive: '지혜로움, 적응력, 공감능력, 통찰력',
        negative: '우울함, 소극성, 과도한 고민',
        core: '깊이 흐르는 지혜와 변화의 에너지'
      }
    };
    
    return traits[dominant];
  },
  
  analyzeCareer: function(balance) {
    const dominant = balance.dominant.element;
    
    const careers = {
      wood: '교육, 예술, 디자인, 환경, 상담, 의료',
      fire: '리더십, 영업, 마케팅, 엔터테인먼트, 정치',
      earth: '부동산, 금융, 건설, 요식업, 서비스업',
      metal: '법률, 회계, 엔지니어링, 군인, 경찰',
      water: '연구, 철학, 예술, 컨설팅, 심리학'
    };
    
    return {
      suitable: careers[dominant],
      advice: balance.harmony.score >= 70 ? 
        '현재 직업에 만족할 가능성이 높습니다' :
        '오행 균형을 맞춰 직업 만족도를 높이세요'
    };
  },
  
  analyzeHealth: function(balance) {
    const dominant = balance.dominant.element;
    
    const health = {
      wood: { vulnerable: '간, 담낭, 눈', advice: '스트레스 관리와 충분한 휴식' },
      fire: { vulnerable: '심장, 혈압, 신경계', advice: '흥분 조절과 마음의 안정' },
      earth: { vulnerable: '위, 소화기, 피부', advice: '규칙적인 식사와 적당한 운동' },
      metal: { vulnerable: '폐, 대장, 호흡기', advice: '공기 좋은 환경과 깊은 호흡' },
      water: { vulnerable: '신장, 방광, 생식기', advice: '충분한 수분 섭취와 보온' }
    };
    
    return health[dominant];
  },
  
  analyzeRelationships: function(balance) {
    const dominant = balance.dominant.element;
    
    const compatibility = {
      wood: { best: 'water', good: 'fire', avoid: 'metal' },
      fire: { best: 'wood', good: 'earth', avoid: 'water' },
      earth: { best: 'fire', good: 'metal', avoid: 'wood' },
      metal: { best: 'earth', good: 'water', avoid: 'fire' },
      water: { best: 'metal', good: 'wood', avoid: 'earth' }
    };
    
    return compatibility[dominant];
  },
  
  generateFortune: function(balance, interactions) {
    const score = balance.harmony.score;
    
    if (score >= 85) {
      return {
        overall: '대길(大吉)',
        message: '오행의 조화가 완벽합니다. 모든 일이 순조롭게 풀릴 것입니다.',
        luck: ['재운 상승', '건강 양호', '대인 관계 원만']
      };
    } else if (score >= 70) {
      return {
        overall: '길(吉)',
        message: '전반적으로 좋은 흐름입니다. 꾸준히 노력하면 성과를 얻을 것입니다.',
        luck: ['안정된 운세', '점진적 발전']
      };
    } else {
      return {
        overall: '평(平)',
        message: '오행 균형을 맞추는 노력이 필요합니다. 추천사항을 따르세요.',
        luck: ['주의 필요', '균형 회복 시급']
      };
    }
  },
  
  generateLifeAdvice: function(balance, interactions) {
    return {
      daily: `매일 ${interactions.recommendation.colors} 계열 옷을 입거나 소품을 활용하세요`,
      workspace: `책상은 ${interactions.recommendation.direction} 방향을 바라보게 배치하세요`,
      hobby: `${interactions.recommendation.strengthenElement} 기운을 보충하는 활동을 찾으세요`,
      mindset: balance.harmony.score >= 70 ?
        '현재의 균형을 유지하며 감사하는 마음을 가지세요' :
        '부족한 오행을 보충하는 데 집중하세요'
    };
  }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SAJU_AI_ENGINE;
}
