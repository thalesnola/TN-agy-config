# Script deterministico para geracao de docs/diagrama-motion.svg
# Compativel 100% com sanitizador do GitHub (SVG Puro sem <filter> e sem style= inline)

import pathlib

SVG_CONTENT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 920" width="1000" height="920">
  <defs>
    <!-- Degradê de fundo suave Motion -->
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F3EEFF"/>
      <stop offset="50%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#E9F7FF"/>
    </linearGradient>

    <!-- Ambient Glows em SVG Puro (substitui feGaussianBlur compatível com GitHub) -->
    <radialGradient id="glow_pink" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FF7AC6" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#FF7AC6" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_blue" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#2F9BFF" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#2F9BFF" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_purple" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_green" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#10B981" stop-opacity="0.20"/>
      <stop offset="100%" stop-color="#10B981" stop-opacity="0"/>
    </radialGradient>

    <!-- Motion Trails Diagonais -->
    <linearGradient id="trail_purple" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8A5CF6" stop-opacity="0"/>
      <stop offset="50%" stop-color="#8A5CF6" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#8A5CF6" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="trail_blue" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#3B82F6" stop-opacity="0"/>
      <stop offset="50%" stop-color="#3B82F6" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#3B82F6" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Fundo -->
  <rect width="1000" height="920" fill="url(#bg)"/>

  <!-- Ambient Glows -->
  <circle cx="910" cy="110" r="230" fill="url(#glow_pink)"/>
  <circle cx="90" cy="790" r="250" fill="url(#glow_blue)"/>
  <circle cx="500" cy="330" r="280" fill="url(#glow_purple)"/>

  <!-- Motion Trails Diagonais (-12deg) -->
  <rect x="120" y="80" width="280" height="26" rx="13" fill="url(#trail_purple)" transform="rotate(-12 260 93)"/>
  <rect x="680" y="440" width="260" height="24" rx="12" fill="url(#trail_blue)" transform="rotate(-12 810 452)"/>
  <rect x="60" y="36" width="324.0" height="26" rx="13" fill="#EDE9FE" stroke="#DDD6FE" stroke-width="1"/>
  <text x="222.0" y="53" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="700" fill="#6D28D9" text-anchor="middle" letter-spacing="0.5">ECOSSISTEMA AGY · CONFIGURAÇÃO UNIFICADA</text><text x="60" y="86" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="26" font-weight="800" fill="#1B1F3B">TN-agy-config · Núcleo Unificado do Antigravity</text><text x="60" y="114" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="14" font-weight="500" fill="#4A5568">Plugins, skills especializadas, 13 servidores MCP, hooks de sessão e perfis multi-estação.</text>
  <!-- Linhas conectoras orbitais -->
  <line x1="500" y1="320" x2="190" y2="190" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="500" y1="320" x2="500" y2="180" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="500" y1="320" x2="810" y2="190" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="500" y1="320" x2="190" y2="450" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="500" y1="320" x2="500" y2="465" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="500" y1="320" x2="810" y2="450" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="4,4"/>
  <rect x="82" y="158" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="81" y="154" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="80" y="150" width="220" height="80" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="92" y="162" width="16" height="16" rx="8" fill="#EDE9FE"/><text x="116" y="175" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#7C3AED">Plugins Oficiais</text><text x="94" y="198" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="94" dy="0">Ecossistemas Google,</tspan><tspan x="94" dy="16">GitHub e Flutter prontos</tspan></text>
  <rect x="392" y="148" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="391" y="144" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="390" y="140" width="220" height="80" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="402" y="152" width="16" height="16" rx="8" fill="#E0F2FE"/><text x="426" y="165" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#0284C7">13 Servidores MCP</text><text x="404" y="188" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="404" dy="0">Filesystem, rag, colab,</tspan><tspan x="404" dy="16">ollama-router e playwright</tspan></text>
  <rect x="702" y="158" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="701" y="154" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="700" y="150" width="220" height="80" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="712" y="162" width="16" height="16" rx="8" fill="#FEF3C7"/><text x="736" y="175" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#D97706">Skills Especializadas</text><text x="714" y="198" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="714" dy="0">Ciência, mídia 3D,</tspan><tspan x="714" dy="16">bigquery e automação</tspan></text>
  <rect x="82" y="418" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="81" y="414" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="80" y="410" width="220" height="80" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="92" y="422" width="16" height="16" rx="8" fill="#DCFCE7"/><text x="116" y="435" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#16A34A">Hooks de Sessão</text><text x="94" y="458" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="94" dy="0">Injeção de contexto e</tspan><tspan x="94" dy="16">verificação de segurança</tspan></text>
  <rect x="392" y="433" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="391" y="429" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="390" y="425" width="220" height="80" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="402" y="437" width="16" height="16" rx="8" fill="#FCE7F3"/><text x="426" y="450" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#DB2777">Ollama Local Serial</text><text x="404" y="473" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="404" dy="0">gpt-oss:20b, Qwen 36GB</tspan><tspan x="404" dy="16">e Nemotron 30B sob mutex</tspan></text>
  <rect x="702" y="418" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="701" y="414" width="220" height="80" rx="16" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="700" y="410" width="220" height="80" rx="16" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/><rect x="712" y="422" width="16" height="16" rx="8" fill="#F1F5F9"/><text x="736" y="435" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#475569">Perfis Multi-Estação</text><text x="714" y="458" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="714" dy="0">Dell Pro Max 16 e</tspan><tspan x="714" dy="16">ambientes integrados</tspan></text>
  <circle cx="500" cy="327" r="68" fill="#1B1F3B" fill-opacity="0.08"/>
  <circle cx="500" cy="320" r="68" fill="#7C3AED" stroke="#6D28D9" stroke-width="3"/><circle cx="500" cy="320" r="60" fill="#6D28D9"/><text x="500" y="312" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="16" font-weight="800" fill="#FFFFFF" text-anchor="middle">AGY CORE</text><text x="500" y="334" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="600" fill="#E9D5FF" text-anchor="middle">Antigravity</text><text x="500" y="348" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="700" fill="#A7F3D0" text-anchor="middle">Gemini 4 Argon</text>
  <!-- BLOCO DE DEMONSTRAÇÃO PRÁTICA -->
  
  <rect x="62" y="563" width="880" height="220" rx="22" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="61" y="559" width="880" height="220" rx="22" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="60" y="555" width="880" height="220" rx="22" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
  
  <rect x="80" y="569" width="225" height="24" rx="12" fill="#1B1F3B"/>
  <text x="192" y="585" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="800" fill="#60A5FA" text-anchor="middle" letter-spacing="0.8">DEMONSTRAÇÃO PRÁTICA</text>
  <text x="320" y="586" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="12" font-weight="600" fill="#64748B">Fluxo operacional concreto do repositório</text>
  
  <!-- Coluna 1: Entrada -->
  
  <rect x="84" y="613" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="83" y="609" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="82" y="605" width="260" height="155" rx="14" fill="#FFFFFF" stroke="#DDD6FE" stroke-width="1.5"/>
  <rect x="94" y="617" width="90" height="20" rx="10" fill="#EDE9FE"/>
  <text x="139" y="631" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#7C3AED" text-anchor="middle">INÍCIO DA SESSÃO</text>
  <text x="96" y="655" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#1B1F3B">Boot do AGY na Estação</text>
  <text x="96" y="675" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="96" dy="0">Usuário inicia o Antigravity em</tspan><tspan x="96" dy="16">ambiente Windows PowerShell 5.1.</tspan><tspan x="96" dy="16">AGY lê configurações unificadas.</tspan></text>
  
  <!-- Seta 1 -> 2 -->
  <circle cx="359" cy="682.5" r="14" fill="#EDE9FE" stroke="#C4B5FD" stroke-width="1.5"/>
  <text x="359" y="687.5" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="800" fill="#7C3AED" text-anchor="middle">→</text>
  
  <!-- Coluna 2: Processamento -->
  
  <rect x="379" y="613" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="378" y="609" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="377" y="605" width="260" height="155" rx="14" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="1.5"/>
  <rect x="389" y="617" width="125" height="20" rx="10" fill="#E0F2FE"/>
  <text x="451" y="631" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#0284C7" text-anchor="middle">ORQUESTRAÇÃO NATIVA</text>
  <text x="391" y="655" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#1B1F3B">Carregamento em Cadeia</text>
  <text x="391" y="675" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="391" dy="0">Hooks carregam AGENTS.md,</tspan><tspan x="391" dy="16">inicializam 13 MCPs locais e</tspan><tspan x="391" dy="16">mapeiam skills sem conflito.</tspan></text>
  
  <!-- Seta 2 -> 3 -->
  <circle cx="654" cy="682.5" r="14" fill="#E0F2FE" stroke="#7DD3FC" stroke-width="1.5"/>
  <text x="654" y="687.5" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="800" fill="#0284C7" text-anchor="middle">→</text>
  
  <!-- Coluna 3: Saída -->
  
  <rect x="674" y="613" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.06"/>
  <rect x="673" y="609" width="260" height="155" rx="14" fill="#1B1F3B" fill-opacity="0.05"/>
  <rect x="672" y="605" width="260" height="155" rx="14" fill="#FFFFFF" stroke="#BBF7D0" stroke-width="1.5"/>
  <rect x="684" y="617" width="105" height="20" rx="10" fill="#DCFCE7"/>
  <text x="736" y="631" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="10" font-weight="800" fill="#16A34A" text-anchor="middle">ESTADO PRONTO</text>
  <text x="686" y="655" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="700" fill="#1B1F3B">Ambiente Endurecido</text>
  <text x="686" y="675" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="400" fill="#475569"><tspan x="686" dy="0">Gemini 4 Argon e Flash 3.8</tspan><tspan x="686" dy="16">operam com ferramentas ativas,</tspan><tspan x="686" dy="16">acesso a repos e LLMs locais.</tspan></text>
  <!-- Faixa Navy Inferior de Conclusão Técnica -->
  <rect x="60" y="800" width="880" height="64" rx="18" fill="#1B1F3B"/>
  <circle cx="95" cy="832" r="15" fill="#3B82F6" fill-opacity="0.25"/>
  <text x="95" y="837" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="15" font-weight="800" fill="#60A5FA" text-anchor="middle">✓</text>
  <text x="125" y="829" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="13" font-weight="800" fill="#FFFFFF">Ambiente Unificado e Produtivo</text>
  <text x="125" y="848" font-family="Segoe UI Variable Display, Segoe UI, sans-serif" font-size="11" font-weight="500" fill="#94A3B8">Configuração canônica garantindo paridade entre estações, MCPs estritamente tipados e zero fricção.</text>
</svg>'''

def main():
    p = pathlib.Path(__file__).parent.parent / 'docs' / 'diagrama-motion.svg'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(SVG_CONTENT, encoding='utf-8')
    print('SVG gerado em:', p)

if __name__ == '__main__':
    main()
