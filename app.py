import streamlit as st
import streamlit.components.v1 as components
import json
import os
import base64
import tempfile
from pathlib import Path
from utils.content_loader import load_chapter, load_scenes

st.set_page_config(
    page_title="WonderLearn",
    page_icon="🌟",
    layout="wide"
)

# ─── TTS Helper ───────────────────────────────────────────────────────────────

@st.cache_data
def generate_tts_audio(text, scene_id):
    """Generate TTS audio for narration text and return base64 encoded audio."""
    try:
        from gtts import gTTS
        import io
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception:
        return None


def render_audio_player(narration_text, scene_id):
    """Render a play narration button with TTS."""
    audio_data = generate_tts_audio(narration_text, scene_id)
    if audio_data:
        st.audio(audio_data, format="audio/mp3")


# ─── CSS Animations & Styling ─────────────────────────────────────────────────

st.markdown("""
<style>

/* ─── Base Layout ─────────────────────────────────────────────────────────── */

.story-container {
    background: white;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-top: 15px;
    margin-bottom: 15px;
}

.dialogue-box {
    background: #F0FDF4;
    border-left: 6px solid #22C55E;
    padding: 20px;
    border-radius: 15px;
    font-size: 18px;
    margin-top: 15px;
    animation: slideInLeft 0.6s ease-out;
}

.speaker {
    font-size: 20px;
    font-weight: bold;
    color: #2563EB;
}

.fun-fact-box {
    background: #FEF9C3;
    border-left: 6px solid #EAB308;
    padding: 15px;
    border-radius: 10px;
    font-size: 16px;
    margin-top: 15px;
    animation: fadeIn 0.8s ease-out;
}

.hotspot-card {
    background: #F8FAFC;
    border: 2px solid #E2E8F0;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
}

.badge-container {
    text-align: center;
    padding: 40px;
    background: linear-gradient(135deg, #FEF9C3, #FDE68A);
    border-radius: 20px;
    margin: 20px 0;
    animation: badgePop 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.badge-icon {
    font-size: 80px;
    animation: bounce 1s ease infinite;
}

.summary-card {
    background: #F0F9FF;
    border-left: 4px solid #3B82F6;
    padding: 15px;
    border-radius: 10px;
    margin: 8px 0;
    animation: slideInLeft 0.5s ease-out;
}

.xp-gain {
    background: #ECFDF5;
    border: 2px solid #22C55E;
    border-radius: 10px;
    padding: 10px 15px;
    text-align: center;
    font-weight: bold;
    color: #16A34A;
}

.quiz-correct {
    background: #DCFCE7;
    border-left: 4px solid #22C55E;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 8px;
}

.quiz-wrong {
    background: #FEE2E2;
    border-left: 4px solid #EF4444;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 8px;
}

.step-card {
    background: #F8FAFC;
    border-radius: 12px;
    padding: 15px;
    margin: 8px 0;
    border-left: 4px solid #8B5CF6;
    animation: slideInLeft 0.5s ease-out;
}

/* ─── Animations ──────────────────────────────────────────────────────────── */

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes badgePop {
    0% { transform: scale(0); opacity: 0; }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); opacity: 1; }
}

@keyframes growUp {
    0% { height: 0; opacity: 0; }
    100% { height: 100%; opacity: 1; }
}

@keyframes float {
    0%, 100% { transform: translateY(0) translateX(0); }
    25% { transform: translateY(-15px) translateX(10px); }
    50% { transform: translateY(-5px) translateX(20px); }
    75% { transform: translateY(-20px) translateX(30px); }
    100% { transform: translateY(0) translateX(40px); }
}

@keyframes waterFlow {
    0% { transform: translateX(0) rotate(0deg); }
    50% { transform: translateX(30px) rotate(5deg); }
    100% { transform: translateX(60px) rotate(-5deg); }
}

@keyframes explode {
    0% { transform: scale(1); }
    50% { transform: scale(1.3); }
    100% { transform: scale(0); opacity: 0; }
}

@keyframes sprout {
    0% { height: 0; opacity: 0; }
    30% { height: 20px; opacity: 0.5; }
    60% { height: 50px; opacity: 0.8; }
    100% { height: 80px; opacity: 1; }
}

/* ─── Process Animation Containers ────────────────────────────────────────── */

.animation-container {
    background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 50%, #7DD3FC 100%);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
    min-height: 200px;
}

.germination-anim {
    background: linear-gradient(180deg, #FEF9C3 0%, #92400E 60%, #78350F 100%);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    text-align: center;
    position: relative;
    min-height: 250px;
}

.seed-icon {
    font-size: 50px;
    animation: bounce 2s ease-in-out infinite;
    display: inline-block;
}

.root-anim {
    font-size: 30px;
    animation: growUp 2s ease-out forwards;
    display: inline-block;
}

.shoot-anim {
    font-size: 40px;
    animation: sprout 3s ease-out forwards;
    display: inline-block;
}

.wind-seed {
    font-size: 30px;
    display: inline-block;
    animation: float 4s ease-in-out infinite;
}

.water-seed {
    font-size: 30px;
    display: inline-block;
    animation: waterFlow 3s ease-in-out infinite;
}

.explode-seed {
    font-size: 30px;
    display: inline-block;
    animation: explode 2s ease-out infinite;
}

/* ─── Farming Timeline ────────────────────────────────────────────────────── */

.timeline-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
}

.timeline-step {
    background: white;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    min-width: 100px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    animation: fadeIn 0.5s ease-out;
    position: relative;
}

.timeline-step::after {
    content: "→";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 20px;
    color: #22C55E;
}

.timeline-step:last-child::after {
    content: "";
}

.timeline-icon {
    font-size: 30px;
    margin-bottom: 5px;
}

/* ─── Seed Anatomy Animation ──────────────────────────────────────────────── */

.seed-anatomy {
    background: linear-gradient(135deg, #FEF3C7, #FDE68A);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
    position: relative;
}

.seed-layer {
    display: inline-block;
    margin: 0 10px;
    text-align: center;
    animation: fadeIn 1s ease-out;
}

.seed-layer-icon {
    font-size: 50px;
    margin-bottom: 8px;
}

.seed-layer-label {
    font-size: 14px;
    font-weight: bold;
    color: #92400E;
}

/* ─── Scene Type Badge ────────────────────────────────────────────────────── */

.scene-type-badge {
    display: inline-block;
    background: #EFF6FF;
    color: #2563EB;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ─── Animation Renderers ──────────────────────────────────────────────────────

def render_interactive_animation(anim_type):
    """Render professional interactive HTML5 Canvas/JS animations with RTL motion."""

    if anim_type == "habitat_types":
        components.html("""
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#f8fafc;margin:0 0 16px;font-size:18px;letter-spacing:0.5px;">Animal Habitats — Where Do They Live?</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#94a3b8;font-size:11px;margin:8px 0 0;">Click any habitat to explore</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;
c.style.width='600px';c.style.height='280px';
ctx.scale(dpr,dpr);
let t=0,selected=-1,hovered=-1;
const habitats=[
  {x:60,y:140,icon:'🦁',label:'Terrestrial',desc:'Land-dwelling animals',bg:'#065f46',glow:'#10b981',examples:'Lion, Elephant, Deer'},
  {x:180,y:140,icon:'🐟',label:'Aquatic',desc:'Live entirely in water',bg:'#1e3a5f',glow:'#3b82f6',examples:'Fish, Whale, Jellyfish'},
  {x:300,y:140,icon:'🐸',label:'Amphibious',desc:'Live on land & water',bg:'#3b0764',glow:'#a855f7',examples:'Frog, Toad, Salamander'},
  {x:420,y:140,icon:'🐒',label:'Arboreal',desc:'Tree-dwelling animals',bg:'#365314',glow:'#84cc16',examples:'Monkey, Koala, Sloth'},
  {x:540,y:140,icon:'🦅',label:'Aerial',desc:'Spend most time flying',bg:'#7c2d12',glow:'#f97316',examples:'Eagle, Hawk, Swift'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=(e.clientX-r.left),my=(e.clientY-r.top);
  selected=-1;
  habitats.forEach((h,i)=>{if(Math.hypot(mx-h.x,my-h.y)<42)selected=i;});
});
c.addEventListener('mousemove',e=>{
  const r=c.getBoundingClientRect();
  const mx=(e.clientX-r.left),my=(e.clientY-r.top);
  hovered=-1;
  habitats.forEach((h,i)=>{if(Math.hypot(mx-h.x,my-h.y)<42)hovered=i;});
  c.style.cursor=hovered>=0?'pointer':'default';
});
function easeOut(x){return 1-Math.pow(1-x,3);}
function draw(){
  ctx.clearRect(0,0,600,280);
  // Floating particles (RTL)
  for(let i=0;i<12;i++){
    let px=600-((t*0.3+i*55)%640),py=30+i*22+Math.sin(t*0.02+i)*10;
    ctx.beginPath();ctx.arc(px,py,1.5,0,Math.PI*2);
    ctx.fillStyle='rgba(148,163,184,0.3)';ctx.fill();
  }
  habitats.forEach((h,i)=>{
    let isActive=selected===i||hovered===i;
    let bounce=Math.sin(t*0.025+i*0.8)*4;
    let scale=isActive?1.12:1;
    ctx.save();ctx.translate(h.x,h.y+bounce);ctx.scale(scale,scale);
    // Glow
    if(isActive){
      ctx.shadowColor=h.glow;ctx.shadowBlur=20;
    }
    // Circle bg
    let grad=ctx.createRadialGradient(0,-10,5,0,0,40);
    grad.addColorStop(0,h.glow+'44');grad.addColorStop(1,h.bg);
    ctx.beginPath();ctx.arc(0,0,40,0,Math.PI*2);
    ctx.fillStyle=grad;ctx.fill();
    ctx.strokeStyle=isActive?h.glow:'rgba(255,255,255,0.15)';
    ctx.lineWidth=isActive?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    // Icon
    ctx.font='34px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(h.icon,0,2);
    ctx.restore();
    // Label
    ctx.font='bold 11px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';ctx.textAlign='center';
    ctx.fillText(h.label,h.x,h.y+bounce+58);
  });
  // Detail panel
  if(selected>=0){
    let h=habitats[selected];
    ctx.fillStyle='rgba(15,23,42,0.9)';
    ctx.beginPath();ctx.roundRect(60,230,480,40,10);ctx.fill();
    ctx.strokeStyle=h.glow;ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='13px "Segoe UI",sans-serif';ctx.fillStyle='#f1f5f9';ctx.textAlign='center';
    ctx.fillText(h.icon+' '+h.desc+' — e.g. '+h.examples,300,254);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=360)
        return True

    elif anim_type == "body_coverings_1":
        components.html("""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#f8fafc;margin:0 0 16px;font-size:18px;">Body Coverings — Nature's Armour</h4>
<canvas id="c" width="600" height="300"></canvas>
<p style="text-align:center;color:#94a3b8;font-size:11px;margin:8px 0 0;">Click to learn about each covering</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=300*dpr;
c.style.width='600px';c.style.height='300px';
ctx.scale(dpr,dpr);
let t=0,selected=-1;
const items=[
  {x:60,y:100,icon:'🪶',name:'Feathers',animal:'Birds',purpose:'Flight + warmth insulation',color:'#fbbf24',bg:'#78350f'},
  {x:180,y:100,icon:'🐍',name:'Scales',animal:'Fish & Reptiles',purpose:'Waterproof protection',color:'#60a5fa',bg:'#1e3a5f'},
  {x:300,y:100,icon:'🐢',name:'Shell',animal:'Tortoise & Snail',purpose:'Portable hard home',color:'#a78bfa',bg:'#3b0764'},
  {x:420,y:100,icon:'🐑',name:'Wool',animal:'Sheep & Yak',purpose:'Traps air for warmth',color:'#f9fafb',bg:'#374151'},
  {x:540,y:100,icon:'🐻‍❄️',name:'Fur/Hair',animal:'Polar Bear & Dog',purpose:'Thick insulation layer',color:'#67e8f9',bg:'#164e63'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  items.forEach((it,i)=>{if(Math.hypot(mx-it.x,my-it.y)<38)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,300);
  items.forEach((it,i)=>{
    let active=selected===i;
    let bounce=Math.sin(t*0.03+i*1.1)*4;
    let s=active?1.15:1;
    ctx.save();ctx.translate(it.x,it.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=it.color;ctx.shadowBlur=18;}
    // Hexagonal-ish card
    ctx.beginPath();ctx.roundRect(-36,-36,72,72,active?18:14);
    let g=ctx.createLinearGradient(-36,-36,36,36);
    g.addColorStop(0,it.bg);g.addColorStop(1,active?it.color+'33':it.bg);
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?it.color:'rgba(255,255,255,0.1)';
    ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='28px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(it.icon,0,0);
    ctx.restore();
    // Name below
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';
    ctx.fillStyle=active?it.color:'#cbd5e1';ctx.textAlign='center';
    ctx.fillText(it.name,it.x,it.y+bounce+52);
    ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#64748b';
    ctx.fillText(it.animal,it.x,it.y+bounce+66);
  });
  // Info panel
  if(selected>=0){
    let it=items[selected];
    ctx.fillStyle='rgba(15,23,42,0.95)';
    ctx.beginPath();ctx.roundRect(50,200,500,70,12);ctx.fill();
    ctx.strokeStyle=it.color+'88';ctx.lineWidth=1.5;ctx.stroke();
    // Animated shine (RTL)
    let shineX=550-((t*3)%550);
    let sg=ctx.createLinearGradient(shineX-30,0,shineX+30,0);
    sg.addColorStop(0,'transparent');sg.addColorStop(0.5,it.color+'22');sg.addColorStop(1,'transparent');
    ctx.fillStyle=sg;ctx.beginPath();ctx.roundRect(50,200,500,70,12);ctx.fill();
    ctx.font='bold 14px "Segoe UI",sans-serif';ctx.fillStyle=it.color;ctx.textAlign='center';
    ctx.fillText(it.icon+' '+it.name,300,225);
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';
    ctx.fillText(it.purpose,300,248);
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#94a3b8';
    ctx.fillText('Found on: '+it.animal,300,265);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=380)
        return True

    elif anim_type == "body_coverings_2":
        components.html("""
<div style="background:linear-gradient(135deg,#1a1a2e,#0f172a);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#f8fafc;margin:0 0 16px;font-size:18px;">Defence Mechanisms — Survive or Perish!</h4>
<canvas id="c" width="600" height="320"></canvas>
<p style="text-align:center;color:#94a3b8;font-size:11px;margin:8px 0 0;">Click to see each defence in action</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=320*dpr;
c.style.width='600px';c.style.height='320px';
ctx.scale(dpr,dpr);
let t=0,selected=-1;
const items=[
  {x:60,y:110,icon:'🦓',name:'Camouflage',desc:'Blends with environment to become invisible to predators',color:'#22c55e',demo:'fade'},
  {x:180,y:110,icon:'🪲',name:'Cuticle',desc:'Hard exoskeleton acts like full-body armour plating',color:'#eab308',demo:'shield'},
  {x:300,y:110,icon:'🦔',name:'Quills/Spines',desc:'Sharp needle-like spines raised when threatened',color:'#ef4444',demo:'spike'},
  {x:420,y:110,icon:'🛡️',name:'Armour Plates',desc:'Armadillo rolls into impenetrable armoured ball',color:'#8b5cf6',demo:'roll'},
  {x:540,y:110,icon:'🦎',name:'Colour Change',desc:'Chameleon changes skin colour to match any surface',color:'#06b6d4',demo:'color'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  items.forEach((it,i)=>{if(Math.hypot(mx-it.x,my-it.y)<40)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,320);
  items.forEach((it,i)=>{
    let active=selected===i;
    let bounce=Math.sin(t*0.03+i*1.2)*4;
    let s=active?1.15:1;
    // Demo effects when active
    if(active&&it.demo==='fade'){
      ctx.globalAlpha=0.3+0.7*Math.abs(Math.sin(t*0.04));
    }
    ctx.save();ctx.translate(it.x,it.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=it.color;ctx.shadowBlur=22;}
    ctx.beginPath();ctx.arc(0,0,38,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-8,4,0,0,38);
    g.addColorStop(0,it.color+'44');g.addColorStop(1,'#1e293b');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?it.color:'rgba(255,255,255,0.12)';
    ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    // Spikes animation
    if(active&&it.demo==='spike'){
      for(let s=0;s<8;s++){
        let angle=s*Math.PI/4+t*0.02;
        let len=38+8+Math.sin(t*0.1+s)*5;
        ctx.beginPath();ctx.moveTo(Math.cos(angle)*38,Math.sin(angle)*38);
        ctx.lineTo(Math.cos(angle)*len,Math.sin(angle)*len);
        ctx.strokeStyle='#ef4444';ctx.lineWidth=2;ctx.stroke();
      }
    }
    ctx.font='30px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(it.icon,0,2);
    ctx.restore();
    ctx.globalAlpha=1;
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';
    ctx.fillStyle=active?it.color:'#cbd5e1';ctx.textAlign='center';
    ctx.fillText(it.name,it.x,it.y+bounce+55);
  });
  // Detail panel
  if(selected>=0){
    let it=items[selected];
    ctx.fillStyle='rgba(15,23,42,0.95)';
    ctx.beginPath();ctx.roundRect(50,220,500,70,12);ctx.fill();
    ctx.strokeStyle=it.color+'66';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='bold 14px "Segoe UI",sans-serif';ctx.fillStyle=it.color;ctx.textAlign='center';
    ctx.fillText(it.icon+' '+it.name+' Defence',300,248);
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';
    ctx.fillText(it.desc,300,268);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=400)
        return True

    elif anim_type == "herbivore_teeth":
        components.html("""
<div style="background:linear-gradient(135deg,#052e16,#14532d);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bbf7d0;margin:0 0 16px;font-size:18px;">Herbivore Digestive Pipeline</h4>
<canvas id="c" width="600" height="260"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=260*dpr;
c.style.width='600px';c.style.height='260px';
ctx.scale(dpr,dpr);
let t=0;
const steps=[
  {x:510,icon:'🌿',label:'Plant Food',sub:'Leaves & Grass',color:'#22c55e'},
  {x:370,icon:'🦷',label:'Incisors',sub:'Bite & Cut',color:'#86efac'},
  {x:230,icon:'⚙️',label:'Flat Molars',sub:'Grind & Crush',color:'#4ade80'},
  {x:90,icon:'🐄',label:'Long Gut',sub:'Slow Digestion',color:'#16a34a'}
];
function draw(){
  ctx.clearRect(0,0,600,260);
  // Pipeline background
  ctx.fillStyle='rgba(5,46,22,0.5)';
  ctx.beginPath();ctx.roundRect(50,75,510,90,20);ctx.fill();
  // Animated food particles (RTL)
  for(let i=0;i<4;i++){
    let px=550-((t*1.2+i*140)%540);
    let py=120+Math.sin(t*0.04+i*2)*8;
    ctx.font='14px serif';ctx.textAlign='center';
    ctx.globalAlpha=0.7;ctx.fillText('🌱',px,py);ctx.globalAlpha=1;
  }
  // Steps
  steps.forEach((s,i)=>{
    let pulse=Math.sin(t*0.04+i*1.5)*3;
    // Connector arrow (RTL)
    if(i<3){
      ctx.beginPath();ctx.moveTo(s.x-35,120);ctx.lineTo(steps[i+1].x+40,120);
      ctx.strokeStyle=s.color+'66';ctx.lineWidth=2;ctx.setLineDash([6,4]);ctx.stroke();ctx.setLineDash([]);
      // Arrow head pointing left
      let ax=steps[i+1].x+42;
      ctx.beginPath();ctx.moveTo(ax+8,115);ctx.lineTo(ax,120);ctx.lineTo(ax+8,125);
      ctx.strokeStyle=s.color;ctx.lineWidth=2;ctx.stroke();
    }
    // Circle
    ctx.save();ctx.translate(s.x,120);
    ctx.shadowColor=s.color;ctx.shadowBlur=12;
    ctx.beginPath();ctx.arc(0,0,32+pulse,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,34);
    g.addColorStop(0,s.color+'66');g.addColorStop(1,'#052e16');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=s.color;ctx.lineWidth=2;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='24px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(s.icon,0,0);
    ctx.restore();
    // Labels
    ctx.font='bold 12px "Segoe UI",sans-serif';ctx.fillStyle='#dcfce7';ctx.textAlign='center';
    ctx.fillText(s.label,s.x,170);
    ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#86efac';
    ctx.fillText(s.sub,s.x,185);
  });
  // Bottom info
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#6ee7b7';ctx.textAlign='center';
  ctx.fillText('🦌 Deer  🐴 Horse  🐄 Cow  🐰 Rabbit — flat teeth for grinding, hard hooves for long walks',300,230);
  // Direction indicator
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#4ade80';ctx.textAlign='right';
  ctx.fillText('Food flows ←',580,50);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=320)
        return True

    elif anim_type == "carnivore_feeders":
        components.html("""
<div style="background:linear-gradient(135deg,#450a0a,#1c1917);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fecaca;margin:0 0 16px;font-size:18px;">Carnivores & Special Feeding Adaptations</h4>
<canvas id="c" width="600" height="300"></canvas>
<p style="text-align:center;color:#a8a29e;font-size:11px;margin:8px 0 0;">Click any animal to explore its feeding tools</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=300*dpr;
c.style.width='600px';c.style.height='300px';
ctx.scale(dpr,dpr);
let t=0,selected=-1;
const items=[
  {x:60,y:100,icon:'🦁',name:'Carnivore',tool:'Sharp canines + Retractable claws',food:'Meat (hunt prey)',color:'#ef4444'},
  {x:180,y:100,icon:'🐻',name:'Omnivore',tool:'Mixed teeth — canines + molars',food:'Plants + Meat (flexible diet)',color:'#f59e0b'},
  {x:300,y:100,icon:'🐿️',name:'Rodent',tool:'Ever-growing gnawing incisors',food:'Nuts, seeds, bark',color:'#22d3ee'},
  {x:420,y:100,icon:'🦋',name:'Proboscis',tool:'Long coiled sucking tube',food:'Flower nectar',color:'#c084fc'},
  {x:540,y:100,icon:'🦟',name:'Piercer',tool:'Needle-like piercing mouthpart',food:'Blood (parasitic)',color:'#f472b6'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  items.forEach((it,i)=>{if(Math.hypot(mx-it.x,my-it.y)<38)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,300);
  // Ambient particles RTL
  for(let i=0;i<8;i++){
    let px=600-((t*0.5+i*80)%650),py=20+i*35+Math.sin(t*0.02+i)*8;
    ctx.beginPath();ctx.arc(px,py,1.2,0,Math.PI*2);
    ctx.fillStyle='rgba(239,68,68,0.2)';ctx.fill();
  }
  items.forEach((it,i)=>{
    let active=selected===i;
    let bounce=Math.sin(t*0.03+i*1.1)*4;
    let s=active?1.18:1;
    ctx.save();ctx.translate(it.x,it.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=it.color;ctx.shadowBlur=20;}
    ctx.beginPath();ctx.arc(0,0,36,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-6,3,0,0,36);
    g.addColorStop(0,it.color+'44');g.addColorStop(1,'#1c1917');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?it.color:'rgba(255,255,255,0.1)';
    ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='28px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(it.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';
    ctx.fillStyle=active?it.color:'#d6d3d1';ctx.textAlign='center';
    ctx.fillText(it.name,it.x,it.y+bounce+52);
  });
  if(selected>=0){
    let it=items[selected];
    ctx.fillStyle='rgba(28,25,23,0.95)';
    ctx.beginPath();ctx.roundRect(40,195,520,85,14);ctx.fill();
    ctx.strokeStyle=it.color+'55';ctx.lineWidth=1.5;ctx.stroke();
    // Animated hunting line RTL
    let hx=560-((t*2)%540);
    ctx.beginPath();ctx.moveTo(hx,195);ctx.lineTo(hx,280);
    ctx.strokeStyle=it.color+'33';ctx.lineWidth=1;ctx.stroke();
    ctx.font='bold 15px "Segoe UI",sans-serif';ctx.fillStyle=it.color;ctx.textAlign='center';
    ctx.fillText(it.icon+' '+it.name,300,220);
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#e7e5e4';
    ctx.fillText('Tool: '+it.tool,300,242);
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#a8a29e';
    ctx.fillText('Diet: '+it.food,300,262);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=380)
        return True

    elif anim_type == "breathing_systems":
        components.html("""
<div style="background:linear-gradient(135deg,#0c1929,#172554);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bfdbfe;margin:0 0 4px;font-size:18px;">How Animals Breathe</h4>
<div id="tabs" style="display:flex;justify-content:center;gap:6px;margin:10px 0;"></div>
<canvas id="c" width="600" height="260"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=260*dpr;
c.style.width='600px';c.style.height='260px';
ctx.scale(dpr,dpr);
let t=0,selected=0;
const systems=[
  {icon:'🫁',name:'Lungs',animal:'Mammals & Birds',flow:['Nostrils','Windpipe','Lungs','O₂ → Blood'],color:'#3b82f6',bgc:'#1e3a5f'},
  {icon:'🐟',name:'Gills',animal:'Fish & Tadpoles',flow:['Water enters mouth','Passes over gills','O₂ extracted','Blood carries O₂'],color:'#10b981',bgc:'#064e3b'},
  {icon:'🦗',name:'Spiracles',animal:'Insects',flow:['Spiracle holes','Trachea tubes','Direct to cells','No blood needed!'],color:'#a855f7',bgc:'#3b0764'},
  {icon:'🪱',name:'Skin',animal:'Earthworm & Frog',flow:['Moist skin surface','O₂ dissolves in','Absorbed into blood','Must stay wet!'],color:'#f59e0b',bgc:'#78350f'},
  {icon:'🐋',name:'Blowhole',animal:'Whales & Dolphins',flow:['Rise to surface','Blowhole opens','Air fills lungs','Dive 30+ min'],color:'#06b6d4',bgc:'#164e63'}
];
// Create tab buttons
const tabsEl=document.getElementById('tabs');
systems.forEach((s,i)=>{
  const btn=document.createElement('button');
  btn.textContent=s.icon+' '+s.name;
  btn.style.cssText='padding:6px 14px;border-radius:20px;border:2px solid '+(i===0?s.color:'#334155')+';background:'+(i===0?s.bgc:'transparent')+';color:'+(i===0?'#f1f5f9':'#94a3b8')+';cursor:pointer;font-size:11px;font-family:inherit;transition:all 0.2s;';
  btn.onmouseenter=()=>{if(i!==selected)btn.style.borderColor='#64748b';};
  btn.onmouseleave=()=>{if(i!==selected)btn.style.borderColor='#334155';};
  btn.onclick=()=>{
    selected=i;
    tabsEl.querySelectorAll('button').forEach((b,j)=>{
      b.style.border='2px solid '+(j===i?systems[j].color:'#334155');
      b.style.background=j===i?systems[j].bgc:'transparent';
      b.style.color=j===i?'#f1f5f9':'#94a3b8';
    });
  };
  tabsEl.appendChild(btn);
});
function draw(){
  ctx.clearRect(0,0,600,260);
  let sys=systems[selected];
  // Title
  ctx.font='14px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';ctx.textAlign='center';
  ctx.fillText(sys.icon+' '+sys.name+' Breathing — '+sys.animal,300,25);
  // Flow boxes RTL layout
  sys.flow.forEach((step,i)=>{
    let x=500-i*130,y=100;
    let progress=(t*0.015)%4;
    let active=Math.floor(progress)===i;
    let glow=active?12:0;
    ctx.save();
    if(active){ctx.shadowColor=sys.color;ctx.shadowBlur=glow;}
    ctx.beginPath();ctx.roundRect(x-55,y-28,110,56,12);
    ctx.fillStyle=active?sys.bgc:'rgba(15,23,42,0.8)';ctx.fill();
    ctx.strokeStyle=active?sys.color:sys.color+'44';
    ctx.lineWidth=active?2:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.restore();
    ctx.font=(active?'bold ':'')+'12px "Segoe UI",sans-serif';
    ctx.fillStyle=active?'#f1f5f9':'#94a3b8';ctx.textAlign='center';
    ctx.fillText(step,x,y+5);
    // Arrow pointing left
    if(i<3){
      let ax=x-58;
      ctx.beginPath();ctx.moveTo(ax+25,y);ctx.lineTo(ax,y);
      ctx.strokeStyle=sys.color+'88';ctx.lineWidth=2;ctx.stroke();
      ctx.beginPath();ctx.moveTo(ax+7,y-4);ctx.lineTo(ax,y);ctx.lineTo(ax+7,y+4);
      ctx.fillStyle=sys.color;ctx.fill();
    }
  });
  // O2 particles flowing RTL
  for(let i=0;i<8;i++){
    let px=580-((t*1.5+i*80)%620),py=170+Math.sin(t*0.025+i)*15;
    ctx.beginPath();ctx.arc(px,py,3,0,Math.PI*2);
    ctx.fillStyle=sys.color+'55';ctx.fill();
    ctx.font='8px sans-serif';ctx.fillStyle=sys.color+'88';ctx.textAlign='center';
    ctx.fillText('O₂',px,py+3);
  }
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#64748b';ctx.textAlign='center';
  ctx.fillText('← Oxygen flows through the respiratory system to body cells',300,235);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=370)
        return True

    elif anim_type == "spiracles_skin":
        components.html("""
<div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#c4b5fd;margin:0 0 16px;font-size:18px;">Spiracles vs Skin Breathing — A Comparison</h4>
<canvas id="c" width="600" height="280"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;
c.style.width='600px';c.style.height='280px';
ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,280);
  // LEFT panel - Insect
  ctx.fillStyle='rgba(30,27,75,0.6)';
  ctx.beginPath();ctx.roundRect(15,10,270,260,14);ctx.fill();
  ctx.strokeStyle='#7c3aed44';ctx.lineWidth=1;ctx.stroke();
  ctx.font='bold 13px "Segoe UI",sans-serif';ctx.fillStyle='#c4b5fd';ctx.textAlign='center';
  ctx.fillText('🦗 Insect — Spiracle System',150,35);
  // Insect body
  ctx.beginPath();ctx.ellipse(150,110,55,25,0,0,Math.PI*2);
  let ig=ctx.createLinearGradient(95,85,205,135);
  ig.addColorStop(0,'#7c3aed');ig.addColorStop(1,'#4c1d95');
  ctx.fillStyle=ig;ctx.fill();ctx.strokeStyle='#a78bfa';ctx.lineWidth=1.5;ctx.stroke();
  // Spiracle holes with pulsing air (RTL)
  for(let i=0;i<5;i++){
    let sx=185-i*20,sy=115;
    let pulse=2+Math.sin(t*0.06+i)*1.5;
    ctx.beginPath();ctx.arc(sx,sy+22,pulse,0,Math.PI*2);
    ctx.fillStyle='#fbbf24';ctx.fill();
    // Air flowing in from right
    let airX=sx+12-Math.abs(Math.sin(t*0.04+i))*10;
    ctx.font='9px serif';ctx.fillText('💨',airX,sy+10);
  }
  // Trachea network
  ctx.setLineDash([2,3]);ctx.strokeStyle='#fbbf2488';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(110,110);ctx.lineTo(190,110);ctx.stroke();
  ctx.beginPath();ctx.moveTo(130,100);ctx.lineTo(130,120);ctx.stroke();
  ctx.beginPath();ctx.moveTo(170,100);ctx.lineTo(170,120);ctx.stroke();
  ctx.setLineDash([]);
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#a78bfa';ctx.textAlign='center';
  ctx.fillText('Spiracle → Trachea → Cells',150,170);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#7c3aed';
  ctx.fillText('No lungs needed!',150,188);
  ctx.fillText('Air reaches cells directly.',150,203);

  // RIGHT panel - Earthworm
  ctx.fillStyle='rgba(30,27,75,0.6)';
  ctx.beginPath();ctx.roundRect(315,10,270,260,14);ctx.fill();
  ctx.strokeStyle='#f59e0b44';ctx.lineWidth=1;ctx.stroke();
  ctx.font='bold 13px "Segoe UI",sans-serif';ctx.fillStyle='#fde68a';ctx.textAlign='center';
  ctx.fillText('🪱 Earthworm — Skin Breathing',450,35);
  // Worm body
  let wormY=110+Math.sin(t*0.025)*4;
  ctx.beginPath();ctx.ellipse(450,wormY,48,16,0,0,Math.PI*2);
  let wg=ctx.createLinearGradient(402,wormY,498,wormY);
  wg.addColorStop(0,'#d97706');wg.addColorStop(0.5,'#fbbf24');wg.addColorStop(1,'#d97706');
  ctx.fillStyle=wg;ctx.fill();ctx.strokeStyle='#f59e0b';ctx.lineWidth=1.5;ctx.stroke();
  // Moisture layer (shimmer RTL)
  for(let i=0;i<6;i++){
    let dx=490-i*16-((t*0.3)%16),dy=wormY-20+Math.sin(t*0.03+i)*3;
    ctx.font='7px serif';ctx.globalAlpha=0.6;ctx.fillText('💧',dx,dy);ctx.globalAlpha=1;
  }
  // O2 arrows going down through skin
  for(let i=0;i<4;i++){
    let ox=425+i*18,progress=(t*0.04+i*0.5)%2;
    let oy=wormY-10+progress*20;
    ctx.font='9px sans-serif';ctx.fillStyle='#60a5fa';ctx.textAlign='center';
    ctx.globalAlpha=1-progress/2;ctx.fillText('O₂',ox,oy);ctx.globalAlpha=1;
  }
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#fde68a';ctx.textAlign='center';
  ctx.fillText('Moist skin → Dissolve O₂ → Blood',450,170);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#f59e0b';
  ctx.fillText('Must stay wet to breathe!',450,188);
  ctx.fillText('Dries out = suffocates.',450,203);

  // VS divider
  ctx.font='bold 16px "Segoe UI",sans-serif';ctx.fillStyle='#64748b';ctx.textAlign='center';
  ctx.fillText('VS',300,120);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "land_movement":
        components.html("""
<div style="background:linear-gradient(135deg,#431407,#1c1917);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fed7aa;margin:0 0 16px;font-size:18px;">How Animals Move on Land</h4>
<canvas id="c" width="600" height="260"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=260*dpr;
c.style.width='600px';c.style.height='260px';
ctx.scale(dpr,dpr);
let t=0;
const animals=[
  {icon:'🐕',y:60,speed:1.2,label:'Walk — 4 legs',color:'#f97316',motion:'walk'},
  {icon:'🦎',y:105,speed:0.6,label:'Crawl — belly low',color:'#84cc16',motion:'crawl'},
  {icon:'🐍',y:145,speed:0.9,label:'Slither — no legs!',color:'#a855f7',motion:'slither'},
  {icon:'🐜',y:185,speed:1.8,label:'Scurry — 6 tiny legs',color:'#22d3ee',motion:'scurry'},
  {icon:'🦘',y:220,speed:1.4,label:'Hop — powerful hind legs',color:'#f472b6',motion:'hop'}
];
function draw(){
  ctx.clearRect(0,0,600,260);
  // Lane backgrounds
  animals.forEach((a,i)=>{
    ctx.fillStyle=i%2===0?'rgba(67,20,7,0.3)':'rgba(28,25,23,0.3)';
    ctx.fillRect(0,a.y-20,600,42);
    // Lane label (right side)
    ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle=a.color+'aa';ctx.textAlign='right';
    ctx.fillText(a.label,590,a.y+5);
  });
  // Animals moving RIGHT to LEFT
  animals.forEach((a,i)=>{
    let x=600-((t*a.speed+i*100)%680)+40;
    let yOff=0;
    if(a.motion==='hop') yOff=-Math.abs(Math.sin(t*0.07))*18;
    if(a.motion==='slither') yOff=Math.sin(t*0.08)*6;
    if(a.motion==='walk') yOff=Math.abs(Math.sin(t*0.1))*3;
    if(a.motion==='scurry') yOff=Math.sin(t*0.15)*2;
    ctx.font='28px serif';ctx.textAlign='center';
    ctx.fillText(a.icon,x,a.y+yOff+8);
    // Motion trail (fading)
    for(let tr=1;tr<=3;tr++){
      ctx.globalAlpha=0.15/tr;
      ctx.fillText(a.icon,x+tr*25,a.y+8);
      ctx.globalAlpha=1;
    }
  });
  // Direction arrow
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#fdba74';ctx.textAlign='center';
  ctx.fillText('← Direction of movement',300,252);
  // Bottom info
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#a8a29e';ctx.textAlign='center';
  ctx.fillText('🐍 Snake: Belly scales + S-shaped muscles + Flexible spine = movement without legs!',300,240);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=330)
        return True

    elif anim_type == "animal_movement":
        components.html("""
<div style="background:linear-gradient(180deg,#0c4a6e 0%,#082f49 45%,#172554 55%,#1e3a5f 100%);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#e0f2fe;margin:0 0 16px;font-size:18px;">Flying & Swimming — Motion Adaptations</h4>
<canvas id="c" width="600" height="300"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=300*dpr;
c.style.width='600px';c.style.height='300px';
ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,300);
  // SKY region
  ctx.fillStyle='rgba(12,74,110,0.3)';ctx.fillRect(0,0,600,140);
  ctx.font='bold 11px "Segoe UI",sans-serif';ctx.fillStyle='#7dd3fc';ctx.textAlign='left';
  ctx.fillText('SKY',15,20);
  // Clouds RTL
  for(let i=0;i<3;i++){
    let cx=600-((t*0.4+i*220)%720);
    ctx.beginPath();ctx.ellipse(cx,30+i*15,30,10,0,0,Math.PI*2);
    ctx.fillStyle='rgba(186,230,253,0.1)';ctx.fill();
  }
  // Bird RTL with wing flap
  let birdX=620-((t*1.3)%700);
  let wingY=Math.sin(t*0.1)*8;
  ctx.font='32px serif';ctx.textAlign='center';
  ctx.fillText('🦅',birdX,65+wingY);
  // Bat RTL
  let batX=620-((t*1.0+250)%700);
  ctx.font='24px serif';ctx.fillText('🦇',batX,100+Math.sin(t*0.08+1)*6);
  // Sky adaptations
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#bae6fd';ctx.textAlign='center';
  ctx.fillText('Hollow bones + Wings + Streamlined body + Tail for steering',300,130);

  // Divider wave
  ctx.beginPath();
  for(let x=0;x<=600;x+=5){
    ctx.lineTo(x,148+Math.sin(x*0.02+t*0.03)*4);
  }
  ctx.strokeStyle='#38bdf844';ctx.lineWidth=2;ctx.stroke();

  // WATER region
  ctx.fillStyle='rgba(23,37,84,0.4)';ctx.fillRect(0,155,600,145);
  ctx.font='bold 11px "Segoe UI",sans-serif';ctx.fillStyle='#67e8f9';ctx.textAlign='left';
  ctx.fillText('WATER',15,172);
  // Fish RTL
  let fishX=630-((t*1.6)%700);
  ctx.font='30px serif';ctx.textAlign='center';
  ctx.fillText('🐠',fishX,200+Math.sin(t*0.05)*4);
  // Duck RTL
  let duckX=630-((t*0.8+300)%700);
  ctx.font='26px serif';ctx.fillText('🦆',duckX,185);
  // Penguin RTL
  let penX=630-((t*1.2+180)%700);
  ctx.font='24px serif';ctx.fillText('🐧',penX,230+Math.sin(t*0.06+2)*4);
  // Bubbles
  for(let i=0;i<5;i++){
    let bx=100+i*120,by=260-((t*0.5+i*40)%100);
    ctx.beginPath();ctx.arc(bx,by,2,0,Math.PI*2);
    ctx.fillStyle='rgba(103,232,249,0.3)';ctx.fill();
  }
  // Water adaptations
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#67e8f9';ctx.textAlign='center';
  ctx.fillText('Fins + Streamlined shape + Webbed feet (duck) + Flippers (penguin)',300,280);
  // Direction
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#7dd3fc55';ctx.textAlign='right';
  ctx.fillText('← movement',590,295);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=370)
        return True

    elif anim_type == "migration_map":
        components.html("""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#e2e8f0;margin:0 0 16px;font-size:18px;">Epic Migration Routes — Thousands of Kilometres!</h4>
<canvas id="c" width="600" height="310"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=310*dpr;
c.style.width='600px';c.style.height='310px';
ctx.scale(dpr,dpr);
let t=0;
const routes=[
  {from:'Siberia',to:'India',animal:'🦢',name:'Siberian Crane',dist:'5,000+ km',y:15,color:'#60a5fa'},
  {from:'Arctic',to:'Antarctic',animal:'🕊️',name:'Arctic Tern',dist:'71,000 km!',y:75,color:'#34d399'},
  {from:'Canada',to:'Mexico',animal:'🦋',name:'Monarch Butterfly',dist:'4,000 km',y:135,color:'#fbbf24'},
  {from:'Open Ocean',to:'Odisha, India',animal:'🐢',name:'Olive Ridley Turtle',dist:'1,000s km',y:195,color:'#f472b6'},
  {from:'River (birth)',to:'Ocean & back',animal:'🐟',name:'Salmon',dist:'Round trip!',y:255,color:'#a78bfa'}
];
function draw(){
  ctx.clearRect(0,0,600,310);
  routes.forEach((r,i)=>{
    // Lane bg
    ctx.fillStyle=i%2===0?'rgba(30,41,59,0.6)':'rgba(15,23,42,0.6)';
    ctx.beginPath();ctx.roundRect(10,r.y,580,52,10);ctx.fill();
    ctx.strokeStyle=r.color+'22';ctx.lineWidth=1;ctx.stroke();
    // From (right side) and To (left side) — RTL migration
    ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#94a3b8';
    ctx.textAlign='right';ctx.fillText(r.from,580,r.y+15);
    ctx.textAlign='left';ctx.fillText(r.to,20,r.y+15);
    // Dotted route line
    ctx.setLineDash([4,6]);ctx.beginPath();
    ctx.moveTo(50,r.y+35);ctx.lineTo(560,r.y+35);
    ctx.strokeStyle=r.color+'44';ctx.lineWidth=1.5;ctx.stroke();ctx.setLineDash([]);
    // Animal moving RTL
    let progress=(t*0.004+i*0.15)%1;
    let animalX=560-progress*510;
    // Trail glow
    ctx.beginPath();
    ctx.moveTo(animalX,r.y+35);ctx.lineTo(animalX+60,r.y+35);
    let tg=ctx.createLinearGradient(animalX,0,animalX+60,0);
    tg.addColorStop(0,r.color+'66');tg.addColorStop(1,'transparent');
    ctx.strokeStyle=tg;ctx.lineWidth=3;ctx.setLineDash([]);ctx.stroke();
    // Animal icon
    ctx.font='20px serif';ctx.textAlign='center';
    ctx.fillText(r.animal,animalX,r.y+41);
    // Name and distance
    ctx.font='bold 11px "Segoe UI",sans-serif';ctx.fillStyle=r.color;ctx.textAlign='center';
    ctx.fillText(r.name+' — '+r.dist,300,r.y+15);
  });
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=390)
        return True

    elif anim_type == "germination_stages":
        components.html("""
<div style="background:linear-gradient(135deg,#1a2e05,#365314);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bbf7d0;margin:0 0 16px;font-size:18px;">Germination — From Seed to Sprout</h4>
<canvas id="c" width="600" height="280"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;
c.style.width='600px';c.style.height='280px';
ctx.scale(dpr,dpr);
let t=0;
const stages=[
  {x:60,label:'Seed',icon:'🌰',desc:'Dormant seed',color:'#a16207'},
  {x:180,label:'Water',icon:'💧',desc:'Absorbs water, swells',color:'#0ea5e9'},
  {x:300,label:'Root',icon:'🌱',desc:'Radicle emerges down',color:'#16a34a'},
  {x:420,label:'Shoot',icon:'🌿',desc:'Plumule grows up',color:'#22c55e'},
  {x:540,label:'Seedling',icon:'🌳',desc:'Leaves open, photosynthesis',color:'#15803d'}
];
function draw(){
  ctx.clearRect(0,0,600,280);
  // Soil line
  ctx.fillStyle='#3f2305';ctx.fillRect(0,180,600,100);
  ctx.fillStyle='#5c3a0a';
  for(let i=0;i<30;i++){ctx.beginPath();ctx.arc(i*20+Math.sin(i)*5,200+Math.random()*60,3,0,Math.PI*2);ctx.fill();}
  // Animated water drops RTL
  for(let i=0;i<5;i++){
    let wx=((t*1.2+i*130)%650)-50,wy=60+Math.sin(t*0.03+i)*20;
    ctx.globalAlpha=0.4;ctx.font='14px serif';ctx.fillText('💧',wx,wy);ctx.globalAlpha=1;
  }
  // Stages
  stages.forEach((s,i)=>{
    let bounce=Math.sin(t*0.03+i*1.2)*4;
    let progress=(t*0.008)%5;
    let active=Math.floor(progress)===i;
    // Growth line connecting stages
    if(i<4){
      ctx.beginPath();ctx.moveTo(s.x+40,130);ctx.lineTo(stages[i+1].x+60,130);
      ctx.strokeStyle=s.color+'44';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);
    }
    ctx.save();ctx.translate(s.x+50,120+bounce);
    if(active){ctx.shadowColor=s.color;ctx.shadowBlur=15;}
    ctx.beginPath();ctx.arc(0,0,30,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,30);
    g.addColorStop(0,s.color+'66');g.addColorStop(1,'#1a2e05');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?s.color:s.color+'66';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='22px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(s.icon,0,0);
    ctx.restore();
    ctx.font='bold 10px "Segoe UI",sans-serif';ctx.fillStyle='#dcfce7';ctx.textAlign='center';
    ctx.fillText(s.label,s.x+50,165);
    ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle='#86efac';
    ctx.fillText(s.desc,s.x+50,178);
  });
  // Direction
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#4ade80';ctx.textAlign='center';
  ctx.fillText('Growth stages progress →',300,260);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=340)
        return True

    elif anim_type == "seed_dispersal":
        components.html("""
<div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bae6fd;margin:0 0 16px;font-size:18px;">Seed Dispersal — How Seeds Travel</h4>
<canvas id="c" width="600" height="300"></canvas>
<p style="text-align:center;color:#94a3b8;font-size:11px;margin:8px 0 0;">Click any method to learn more</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=300*dpr;
c.style.width='600px';c.style.height='300px';
ctx.scale(dpr,dpr);
let t=0,selected=-1;
const methods=[
  {x:60,y:100,icon:'💨',name:'Wind',desc:'Light seeds with wings/parachutes float away',examples:'Dandelion, Maple, Cotton',color:'#7dd3fc'},
  {x:180,y:100,icon:'🌊',name:'Water',desc:'Waterproof seeds float to new locations',examples:'Coconut, Lotus, Water lily',color:'#22d3ee'},
  {x:300,y:100,icon:'🐿️',name:'Animals',desc:'Eaten or stuck to fur, carried far away',examples:'Berries, Burrs, Mango',color:'#fbbf24'},
  {x:420,y:100,icon:'💥',name:'Explosion',desc:'Pod bursts open, flinging seeds outward',examples:'Pea, Balsam, Touch-me-not',color:'#f87171'},
  {x:540,y:100,icon:'👨‍🌾',name:'Humans',desc:'Farmers plant and spread seeds deliberately',examples:'Wheat, Rice, Vegetables',color:'#a78bfa'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  methods.forEach((m,i)=>{if(Math.hypot(mx-m.x,my-m.y)<38)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,300);
  // Floating seeds RTL
  for(let i=0;i<6;i++){
    let sx=((t*0.8+i*110)%680)-40,sy=30+i*15+Math.sin(t*0.02+i)*12;
    ctx.globalAlpha=0.3;ctx.font='12px serif';ctx.fillText('🌱',sx,sy);ctx.globalAlpha=1;
  }
  methods.forEach((m,i)=>{
    let active=selected===i;
    let bounce=Math.sin(t*0.03+i*1.1)*4;
    let s=active?1.15:1;
    ctx.save();ctx.translate(m.x,m.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=m.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.arc(0,0,35,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,35);
    g.addColorStop(0,m.color+'44');g.addColorStop(1,'#0f172a');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?m.color:'rgba(255,255,255,0.12)';
    ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='26px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(m.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';
    ctx.fillStyle=active?m.color:'#cbd5e1';ctx.textAlign='center';
    ctx.fillText(m.name,m.x,m.y+bounce+52);
  });
  if(selected>=0){
    let m=methods[selected];
    ctx.fillStyle='rgba(15,23,42,0.95)';ctx.beginPath();ctx.roundRect(50,195,500,80,12);ctx.fill();
    ctx.strokeStyle=m.color+'55';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='bold 14px "Segoe UI",sans-serif';ctx.fillStyle=m.color;ctx.textAlign='center';
    ctx.fillText(m.icon+' Dispersal by '+m.name,300,220);
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';
    ctx.fillText(m.desc,300,242);
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#94a3b8';
    ctx.fillText('Examples: '+m.examples,300,262);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=380)
        return True

    elif anim_type == "seed_anatomy":
        components.html("""
<div style="background:linear-gradient(135deg,#1c1917,#431407);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fed7aa;margin:0 0 16px;font-size:18px;">Inside a Seed — Parts & Functions</h4>
<canvas id="c" width="600" height="300"></canvas>
<p style="text-align:center;color:#a8a29e;font-size:11px;margin:8px 0 0;">Click each part to learn its role</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=300*dpr;
c.style.width='600px';c.style.height='300px';
ctx.scale(dpr,dpr);
let t=0,selected=-1;
const parts=[
  {x:300,y:90,r:60,label:'Seed Coat',desc:'Tough outer layer — protects the seed from damage, insects & drying out',color:'#d97706',icon:'🛡️'},
  {x:300,y:160,r:35,label:'Cotyledon',desc:'Food storage — provides energy to baby plant until it can make its own food',color:'#65a30d',icon:'🍽️'},
  {x:300,y:220,r:20,label:'Embryo',desc:'Baby plant inside — has tiny root (radicle) and tiny shoot (plumule)',color:'#dc2626',icon:'🌱'},
  {x:480,y:120,r:25,label:'Micropyle',desc:'Tiny hole — lets water enter the seed to start germination',color:'#0ea5e9',icon:'💧'},
  {x:480,y:200,r:25,label:'Hilum',desc:'Scar where seed was attached to fruit — like a belly button!',color:'#a855f7',icon:'⭕'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  parts.forEach((p,i)=>{if(Math.hypot(mx-p.x,my-p.y)<p.r+5)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,300);
  // Draw seed outline
  ctx.beginPath();ctx.ellipse(300,155,80,95,0,0,Math.PI*2);
  ctx.fillStyle='#78350f';ctx.fill();ctx.strokeStyle='#d97706';ctx.lineWidth=2;ctx.stroke();
  // Parts
  parts.forEach((p,i)=>{
    let active=selected===i;
    let pulse=active?3+Math.sin(t*0.08)*3:0;
    ctx.save();
    if(active){ctx.shadowColor=p.color;ctx.shadowBlur=15;}
    ctx.beginPath();ctx.arc(p.x,p.y,p.r+pulse,0,Math.PI*2);
    ctx.fillStyle=p.color+'33';ctx.fill();
    ctx.strokeStyle=active?p.color:p.color+'88';
    ctx.lineWidth=active?2.5:1.5;ctx.setLineDash(active?[]:[3,3]);ctx.stroke();ctx.setLineDash([]);
    ctx.shadowBlur=0;ctx.restore();
    // Label
    let lx=p.x<200?p.x-50:p.x>400?p.x+0:p.x;
    ctx.font=(active?'bold ':'')+' 10px "Segoe UI",sans-serif';
    ctx.fillStyle=active?p.color:'#d6d3d1';ctx.textAlign='center';
    ctx.fillText(p.label,lx,p.y+p.r+14);
  });
  // Info panel
  if(selected>=0){
    let p=parts[selected];
    ctx.fillStyle='rgba(28,25,23,0.95)';ctx.beginPath();ctx.roundRect(30,255,540,40,8);ctx.fill();
    ctx.strokeStyle=p.color+'55';ctx.lineWidth=1;ctx.stroke();
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#fafaf9';ctx.textAlign='center';
    ctx.fillText(p.icon+' '+p.label+': '+p.desc,300,280);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=370)
        return True

    elif anim_type == "stem_cutting":
        components.html("""
<div style="background:linear-gradient(135deg,#052e16,#14532d);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bbf7d0;margin:0 0 16px;font-size:18px;">Vegetative Propagation — Growing Without Seeds</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#86efac;font-size:11px;margin:8px 0 0;">Click each method to see how it works</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;
c.style.width='600px';c.style.height='280px';
ctx.scale(dpr,dpr);
let t=0,selected=-1;
const methods=[
  {x:75,y:100,icon:'✂️',name:'Stem Cutting',desc:'Cut a stem, plant in soil → roots grow from the cut end',plant:'Rose, Sugarcane, Money plant',color:'#22c55e'},
  {x:210,y:100,icon:'🥔',name:'Tuber',desc:'Underground stem with buds (eyes) — each bud grows a new plant',plant:'Potato, Ginger',color:'#eab308'},
  {x:345,y:100,icon:'🧅',name:'Bulb',desc:'Layered underground bud — splits into baby bulbs',plant:'Onion, Garlic, Tulip',color:'#f97316'},
  {x:480,y:100,icon:'🌿',name:'Runner/Stolon',desc:'Horizontal stem runs along ground, roots at nodes',plant:'Strawberry, Grass, Spider plant',color:'#06b6d4'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();
  const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  methods.forEach((m,i)=>{if(Math.hypot(mx-m.x,my-m.y)<40)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,280);
  // Soil
  ctx.fillStyle='#1a0f00';ctx.fillRect(0,200,600,80);
  // Growing roots animation
  if(selected>=0){
    let m=methods[selected];
    for(let i=0;i<4;i++){
      let rx=m.x-15+i*10,ry=200+((t*0.5+i*8)%50);
      ctx.beginPath();ctx.moveTo(m.x,200);ctx.quadraticCurveTo(rx,ry-10,rx,ry);
      ctx.strokeStyle=m.color+'66';ctx.lineWidth=1.5;ctx.stroke();
    }
  }
  methods.forEach((m,i)=>{
    let active=selected===i;
    let bounce=Math.sin(t*0.03+i*1.2)*4;
    let s=active?1.15:1;
    ctx.save();ctx.translate(m.x,m.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=m.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.roundRect(-35,-35,70,70,16);
    let g=ctx.createLinearGradient(-35,-35,35,35);
    g.addColorStop(0,m.color+'33');g.addColorStop(1,'#052e16');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?m.color:'rgba(255,255,255,0.1)';
    ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='28px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(m.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 10px "Segoe UI",sans-serif';
    ctx.fillStyle=active?m.color:'#bbf7d0';ctx.textAlign='center';
    ctx.fillText(m.name,m.x,m.y+bounce+52);
  });
  if(selected>=0){
    let m=methods[selected];
    ctx.fillStyle='rgba(5,46,22,0.95)';ctx.beginPath();ctx.roundRect(40,155,520,42,8);ctx.fill();
    ctx.strokeStyle=m.color+'44';ctx.lineWidth=1;ctx.stroke();
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#dcfce7';ctx.textAlign='center';
    ctx.fillText(m.desc,300,172);
    ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#86efac';
    ctx.fillText('Plants: '+m.plant,300,188);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "agriculture_timeline":
        components.html("""
<div style="background:linear-gradient(135deg,#422006,#1c1917);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fde68a;margin:0 0 16px;font-size:18px;">Agriculture — From Ploughing to Harvest</h4>
<canvas id="c" width="600" height="260"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=260*dpr;
c.style.width='600px';c.style.height='260px';
ctx.scale(dpr,dpr);
let t=0;
const steps=[
  {x:60,icon:'🚜',label:'Ploughing',desc:'Loosen soil',color:'#d97706'},
  {x:180,icon:'🌱',label:'Sowing',desc:'Plant seeds',color:'#16a34a'},
  {x:300,icon:'💧',label:'Irrigation',desc:'Water crops',color:'#0ea5e9'},
  {x:420,icon:'🧴',label:'Fertilizing',desc:'Add nutrients',color:'#a855f7'},
  {x:540,icon:'🌾',label:'Harvesting',desc:'Collect crops',color:'#eab308'}
];
function draw(){
  ctx.clearRect(0,0,600,260);
  // Timeline line
  ctx.beginPath();ctx.moveTo(550,120);ctx.lineTo(50,120);
  ctx.strokeStyle='#92400e44';ctx.lineWidth=3;ctx.stroke();
  // Animated farmer walking RTL
  let farmerX=((t*1)%620)-20;
  ctx.font='24px serif';ctx.textAlign='center';ctx.fillText('👨‍🌾',farmerX,90);
  // Steps
  steps.forEach((s,i)=>{
    let progress=(t*0.012)%5;
    let active=Math.floor(progress)===i;
    let bounce=Math.sin(t*0.03+i)*4;
    ctx.save();ctx.translate(s.x,120+bounce);
    if(active){ctx.shadowColor=s.color;ctx.shadowBlur=14;}
    ctx.beginPath();ctx.arc(0,0,28,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-4,2,0,0,28);
    g.addColorStop(0,s.color+'55');g.addColorStop(1,'#1c1917');
    ctx.fillStyle=g;ctx.fill();
    ctx.strokeStyle=active?s.color:s.color+'66';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;
    ctx.font='20px serif';ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(s.icon,0,0);
    ctx.restore();
    // Arrow between steps (RTL)
    if(i<4){
      let ax=s.x-32;
      ctx.beginPath();ctx.moveTo(ax,120);ctx.lineTo(ax-18,120);
      ctx.strokeStyle=s.color+'88';ctx.lineWidth=2;ctx.stroke();
      ctx.beginPath();ctx.moveTo(ax-14,116);ctx.lineTo(ax-20,120);ctx.lineTo(ax-14,124);
      ctx.fillStyle=s.color;ctx.fill();
    }
    ctx.font='bold 10px "Segoe UI",sans-serif';ctx.fillStyle='#fde68a';ctx.textAlign='center';
    ctx.fillText(s.label,s.x,163+bounce);
    ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle='#fbbf24';
    ctx.fillText(s.desc,s.x,177+bounce);
  });
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#d97706';ctx.textAlign='center';
  ctx.fillText('Farming cycle progresses through seasons →',300,240);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=330)
        return True

    elif anim_type == "skeleton_functions":
        components.html("""
<div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#c4b5fd;margin:0 0 16px;font-size:18px;">Skeleton — 5 Vital Functions</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#a5b4fc;font-size:11px;margin:8px 0 0;">Click each function to explore</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const funcs=[
  {x:60,y:100,icon:'🏗️',name:'Support',desc:'Framework that holds body upright — like a building frame',color:'#818cf8'},
  {x:180,y:100,icon:'🛡️',name:'Protection',desc:'Skull protects brain, ribs protect heart & lungs',color:'#f472b6'},
  {x:300,y:100,icon:'🏃',name:'Movement',desc:'Bones + joints + muscles work together for motion',color:'#34d399'},
  {x:420,y:100,icon:'🩸',name:'Blood Cells',desc:'Bone marrow inside bones makes red & white blood cells',color:'#f87171'},
  {x:540,y:100,icon:'🏦',name:'Mineral Store',desc:'Stores calcium & phosphorus, releases when body needs them',color:'#fbbf24'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  funcs.forEach((f,i)=>{if(Math.hypot(mx-f.x,my-f.y)<36)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,280);
  for(let i=0;i<8;i++){let px=600-((t*0.4+i*80)%660),py=20+i*30+Math.sin(t*0.02+i)*8;ctx.beginPath();ctx.arc(px,py,1.5,0,Math.PI*2);ctx.fillStyle='rgba(165,180,252,0.2)';ctx.fill();}
  funcs.forEach((f,i)=>{
    let active=selected===i;let bounce=Math.sin(t*0.03+i*1.1)*4;let s=active?1.15:1;
    ctx.save();ctx.translate(f.x,f.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=f.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.arc(0,0,34,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,34);g.addColorStop(0,f.color+'44');g.addColorStop(1,'#1e1b4b');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?f.color:'rgba(255,255,255,0.1)';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='26px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(f.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 10px "Segoe UI",sans-serif';ctx.fillStyle=active?f.color:'#c4b5fd';ctx.textAlign='center';ctx.fillText(f.name,f.x,f.y+bounce+50);
  });
  if(selected>=0){let f=funcs[selected];
    ctx.fillStyle='rgba(30,27,75,0.95)';ctx.beginPath();ctx.roundRect(50,200,500,55,10);ctx.fill();
    ctx.strokeStyle=f.color+'55';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='bold 13px "Segoe UI",sans-serif';ctx.fillStyle=f.color;ctx.textAlign='center';ctx.fillText(f.icon+' '+f.name,300,222);
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';ctx.fillText(f.desc,300,242);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "bone_structure":
        components.html("""
<div style="background:linear-gradient(135deg,#1c1917,#292524);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fef3c7;margin:0 0 16px;font-size:18px;">Inside a Bone — Layers of Strength</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#a8a29e;font-size:11px;margin:8px 0 0;">Click each layer to learn about it</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const layers=[
  {y:60,h:40,label:'Periosteum',desc:'Thin outer membrane — has nerves (why broken bones hurt!) & blood vessels',color:'#fbbf24'},
  {y:110,h:50,label:'Compact Bone',desc:'Hard dense outer layer — gives bone its strength and white colour',color:'#f5f5f4'},
  {y:170,h:50,label:'Spongy Bone',desc:'Honeycomb-like structure — lightweight but strong, found at bone ends',color:'#fca5a5'},
  {y:230,h:35,label:'Bone Marrow',desc:'Soft tissue in centre — makes 200 billion new blood cells every day!',color:'#f87171'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();const my=e.clientY-r.top;
  let prev=selected;selected=-1;
  layers.forEach((l,i)=>{if(my>=l.y&&my<=l.y+l.h)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,280);
  // Bone shape
  ctx.beginPath();ctx.roundRect(150,50,300,225,30);ctx.fillStyle='#44403c';ctx.fill();
  layers.forEach((l,i)=>{
    let active=selected===i;
    let glow=active?8:0;
    ctx.save();
    if(active){ctx.shadowColor=l.color;ctx.shadowBlur=glow;}
    ctx.beginPath();ctx.roundRect(160,l.y,280,l.h,6);
    ctx.fillStyle=active?l.color+'55':l.color+'22';ctx.fill();
    ctx.strokeStyle=active?l.color:l.color+'66';ctx.lineWidth=active?2:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.restore();
    // Label
    ctx.font=(active?'bold ':'')+' 12px "Segoe UI",sans-serif';
    ctx.fillStyle=active?l.color:'#d6d3d1';ctx.textAlign='left';
    ctx.fillText(l.label,470,l.y+l.h/2+4);
    // Pointer line
    ctx.beginPath();ctx.moveTo(440,l.y+l.h/2);ctx.lineTo(465,l.y+l.h/2);
    ctx.strokeStyle=l.color+'88';ctx.lineWidth=1;ctx.stroke();
  });
  // Spongy honeycomb pattern
  if(selected===2||selected===-1){
    for(let i=0;i<8;i++){
      let hx=200+i*30,hy=185+Math.sin(i)*8;
      ctx.beginPath();ctx.arc(hx,hy,6,0,Math.PI*2);
      ctx.strokeStyle='#fca5a544';ctx.lineWidth=1;ctx.stroke();
    }
  }
  // Info
  if(selected>=0){
    let l=layers[selected];
    ctx.fillStyle='rgba(28,25,23,0.95)';ctx.beginPath();ctx.roundRect(20,2,130,40,8);ctx.fill();
    ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#fafaf9';ctx.textAlign='left';
    let words=l.desc.split(' '),line='',ly=18;
    words.forEach(w=>{if((line+w).length>30){ctx.fillText(line,30,ly);ly+=13;line=w+' ';}else line+=w+' ';});
    ctx.fillText(line,30,ly);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "skull_parts":
        components.html("""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#e2e8f0;margin:0 0 16px;font-size:18px;">The Skull — Cranium + Face Bones</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#94a3b8;font-size:11px;margin:8px 0 0;">Click parts of the skull</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const parts=[
  {x:200,y:80,r:55,name:'Cranium',desc:'8 fused bones forming dome — protects the brain',color:'#818cf8',icon:'🧠'},
  {x:200,y:175,r:30,name:'Face Bones',desc:'14 bones — jaw is the only movable skull bone',color:'#f472b6',icon:'😊'},
  {x:200,y:220,r:15,name:'Jaw (Mandible)',desc:'Lower jaw — only bone in skull that moves! For chewing & talking',color:'#fbbf24',icon:'🗣️'},
  {x:400,y:100,r:25,name:'Eye Sockets',desc:'2 bony cups — protect your delicate eyeballs',color:'#22d3ee',icon:'👁️'},
  {x:400,y:180,r:25,name:'Foramen Magnum',desc:'Hole at skull base — spinal cord passes through here',color:'#f87171',icon:'⭕'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  parts.forEach((p,i)=>{if(Math.hypot(mx-p.x,my-p.y)<p.r)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,280);
  // Skull outline
  ctx.beginPath();ctx.ellipse(200,130,70,100,0,0,Math.PI*2);
  ctx.fillStyle='#334155';ctx.fill();ctx.strokeStyle='#64748b';ctx.lineWidth=2;ctx.stroke();
  parts.forEach((p,i)=>{
    let active=selected===i;let pulse=active?Math.sin(t*0.06)*3:0;
    ctx.save();
    if(active){ctx.shadowColor=p.color;ctx.shadowBlur=14;}
    ctx.beginPath();ctx.arc(p.x,p.y,p.r+pulse,0,Math.PI*2);
    ctx.fillStyle=active?p.color+'33':'transparent';ctx.fill();
    ctx.strokeStyle=active?p.color:p.color+'66';ctx.lineWidth=active?2.5:1.5;ctx.setLineDash(active?[]:[3,3]);ctx.stroke();ctx.setLineDash([]);
    ctx.shadowBlur=0;ctx.restore();
    if(p.x>300){ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle=p.color;ctx.textAlign='center';ctx.fillText(p.name,p.x,p.y+p.r+14);}
  });
  // Labels on left
  ctx.font='10px "Segoe UI",sans-serif';ctx.textAlign='right';
  ctx.fillStyle='#818cf8';ctx.fillText('Cranium',110,80);
  ctx.fillStyle='#f472b6';ctx.fillText('Face',110,175);
  ctx.fillStyle='#fbbf24';ctx.fillText('Jaw',110,220);
  if(selected>=0){
    let p=parts[selected];
    ctx.fillStyle='rgba(15,23,42,0.95)';ctx.beginPath();ctx.roundRect(50,248,500,28,6);ctx.fill();
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#f1f5f9';ctx.textAlign='center';
    ctx.fillText(p.icon+' '+p.name+': '+p.desc,300,266);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "skeleton_parts":
        components.html("""
<div style="background:linear-gradient(135deg,#0c1929,#1e293b);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bae6fd;margin:0 0 16px;font-size:18px;">206 Bones — Major Parts of the Skeleton</h4>
<canvas id="c" width="600" height="300"></canvas>
<p style="text-align:center;color:#94a3b8;font-size:11px;margin:8px 0 0;">Click a region to learn about it</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=300*dpr;c.style.width='600px';c.style.height='300px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const regions=[
  {x:60,y:90,icon:'💀',name:'Skull (22)',desc:'Protects brain — 8 cranium + 14 face bones',color:'#818cf8'},
  {x:180,y:90,icon:'🦴',name:'Spine (33)',desc:'Backbone — 33 vertebrae stacked, protects spinal cord',color:'#34d399'},
  {x:300,y:90,icon:'🫁',name:'Rib Cage (24)',desc:'12 pairs of curved bones — protects heart & lungs',color:'#f472b6'},
  {x:420,y:90,icon:'💪',name:'Arms (60)',desc:'Shoulder to fingers — humerus, radius, ulna + 27 hand bones each',color:'#fbbf24'},
  {x:540,y:90,icon:'🦵',name:'Legs (60)',desc:'Hip to toes — femur (longest bone!), tibia, fibula + 26 foot bones',color:'#f87171'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  regions.forEach((rg,i)=>{if(Math.hypot(mx-rg.x,my-rg.y)<36)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,300);
  // Stick figure in center background
  ctx.strokeStyle='#334155';ctx.lineWidth=2;
  ctx.beginPath();ctx.arc(300,60,15,0,Math.PI*2);ctx.stroke();
  ctx.beginPath();ctx.moveTo(300,75);ctx.lineTo(300,160);ctx.stroke();
  ctx.beginPath();ctx.moveTo(300,95);ctx.lineTo(260,130);ctx.moveTo(300,95);ctx.lineTo(340,130);ctx.stroke();
  ctx.beginPath();ctx.moveTo(300,160);ctx.lineTo(270,220);ctx.moveTo(300,160);ctx.lineTo(330,220);ctx.stroke();
  regions.forEach((rg,i)=>{
    let active=selected===i;let bounce=Math.sin(t*0.03+i*1.1)*3;let s=active?1.12:1;
    ctx.save();ctx.translate(rg.x,rg.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=rg.color;ctx.shadowBlur=16;}
    ctx.beginPath();ctx.arc(0,0,33,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-4,2,0,0,33);g.addColorStop(0,rg.color+'44');g.addColorStop(1,'#0c1929');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?rg.color:'rgba(255,255,255,0.1)';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='24px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(rg.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 10px "Segoe UI",sans-serif';ctx.fillStyle=active?rg.color:'#bae6fd';ctx.textAlign='center';ctx.fillText(rg.name,rg.x,rg.y+bounce+48);
  });
  if(selected>=0){let rg=regions[selected];
    ctx.fillStyle='rgba(12,25,41,0.95)';ctx.beginPath();ctx.roundRect(50,240,500,45,10);ctx.fill();
    ctx.strokeStyle=rg.color+'44';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='bold 12px "Segoe UI",sans-serif';ctx.fillStyle=rg.color;ctx.textAlign='center';ctx.fillText(rg.icon+' '+rg.name,300,258);
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#e2e8f0';ctx.fillText(rg.desc,300,276);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=370)
        return True

    elif anim_type == "ball_socket_joint":
        components.html("""
<div style="background:linear-gradient(135deg,#064e3b,#065f46);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#6ee7b7;margin:0 0 16px;font-size:18px;">Ball & Socket Joint — Full Rotation!</h4>
<canvas id="c" width="600" height="280"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,280);
  // Socket (cup)
  ctx.beginPath();ctx.arc(200,150,60,0.3*Math.PI,0.7*Math.PI);
  ctx.strokeStyle='#a7f3d0';ctx.lineWidth=8;ctx.lineCap='round';ctx.stroke();
  ctx.beginPath();ctx.arc(200,150,60,-0.7*Math.PI,-0.3*Math.PI);
  ctx.strokeStyle='#a7f3d0';ctx.lineWidth=8;ctx.stroke();
  // Ball rotating in socket
  let angle=t*0.02;
  let bx=200+Math.cos(angle)*5,by=150+Math.sin(angle)*5;
  ctx.beginPath();ctx.arc(bx,by,30,0,Math.PI*2);
  ctx.fillStyle='#34d399';ctx.fill();ctx.strokeStyle='#6ee7b7';ctx.lineWidth=2;ctx.stroke();
  // Arm bone attached to ball, rotating
  let armAngle=Math.sin(t*0.015)*1.2;
  let armEndX=bx+Math.cos(armAngle)*100;
  let armEndY=by+Math.sin(armAngle)*100;
  ctx.beginPath();ctx.moveTo(bx,by);ctx.lineTo(armEndX,armEndY);
  ctx.strokeStyle='#fef3c7';ctx.lineWidth=12;ctx.lineCap='round';ctx.stroke();
  // Rotation arrows
  ctx.beginPath();ctx.arc(200,150,80,0,Math.PI*1.5);
  ctx.strokeStyle='#6ee7b766';ctx.lineWidth=2;ctx.setLineDash([5,5]);ctx.stroke();ctx.setLineDash([]);
  // Labels
  ctx.font='bold 12px "Segoe UI",sans-serif';ctx.fillStyle='#6ee7b7';ctx.textAlign='center';
  ctx.fillText('Socket (Cup)',200,240);
  ctx.fillText('Ball (Head)',200,110);
  // Info on right
  ctx.font='13px "Segoe UI",sans-serif';ctx.fillStyle='#d1fae5';ctx.textAlign='left';
  ctx.fillText('🔄 Allows movement in ALL directions',350,100);
  ctx.fillText('📍 Found at: Shoulder & Hip',350,125);
  ctx.fillText('💡 Ball-shaped end fits into cup-shaped socket',350,150);
  ctx.fillText('🏃 Lets you swing arms, rotate legs',350,175);
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#6ee7b7';
  ctx.fillText('Most flexible joint in the body!',350,210);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "hinge_joint":
        components.html("""
<div style="background:linear-gradient(135deg,#7c2d12,#431407);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fed7aa;margin:0 0 16px;font-size:18px;">Hinge Joint — Like a Door!</h4>
<canvas id="c" width="600" height="280"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,280);
  // Upper bone (fixed)
  ctx.beginPath();ctx.moveTo(180,50);ctx.lineTo(180,140);
  ctx.strokeStyle='#fef3c7';ctx.lineWidth=14;ctx.lineCap='round';ctx.stroke();
  // Hinge point
  ctx.beginPath();ctx.arc(180,145,12,0,Math.PI*2);
  ctx.fillStyle='#f97316';ctx.fill();ctx.strokeStyle='#fed7aa';ctx.lineWidth=2;ctx.stroke();
  // Lower bone (swinging)
  let angle=Math.sin(t*0.025)*0.8+0.4;
  let endX=180+Math.sin(angle)*100;
  let endY=145+Math.cos(angle)*100;
  ctx.beginPath();ctx.moveTo(180,145);ctx.lineTo(endX,endY);
  ctx.strokeStyle='#fde68a';ctx.lineWidth=12;ctx.lineCap='round';ctx.stroke();
  // Arc showing range
  ctx.beginPath();ctx.arc(180,145,50,-0.4,1.2);
  ctx.strokeStyle='#f9731666';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);
  // Door comparison on right
  ctx.fillStyle='#78350f';ctx.fillRect(380,60,10,180);
  let doorAngle=Math.sin(t*0.025)*0.7;
  ctx.save();ctx.translate(390,150);ctx.rotate(doorAngle);
  ctx.fillStyle='#d97706';ctx.fillRect(0,-70,80,140);
  ctx.fillStyle='#fbbf24';ctx.beginPath();ctx.arc(65,0,5,0,Math.PI*2);ctx.fill();
  ctx.restore();
  // Labels
  ctx.font='bold 12px "Segoe UI",sans-serif';ctx.fillStyle='#fed7aa';ctx.textAlign='center';
  ctx.fillText('Elbow / Knee',180,265);
  ctx.fillText('Door Hinge',420,265);
  ctx.font='13px "Segoe UI",sans-serif';ctx.fillStyle='#fde68a';ctx.textAlign='left';
  ctx.fillText('↕️ Only bends ONE direction',350,40);
  ctx.fillText('📍 Elbow, Knee, Fingers',350,60);
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#fdba74';
  ctx.fillText('Cannot rotate — just open & close!',180,280);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "pivot_gliding_joint":
        components.html("""
<div style="background:linear-gradient(135deg,#172554,#1e3a5f);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bfdbfe;margin:0 0 16px;font-size:18px;">Pivot & Gliding Joints</h4>
<canvas id="c" width="600" height="280"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,280);
  // LEFT - Pivot Joint
  ctx.fillStyle='rgba(23,37,84,0.5)';ctx.beginPath();ctx.roundRect(15,10,270,260,14);ctx.fill();
  ctx.strokeStyle='#3b82f644';ctx.lineWidth=1;ctx.stroke();
  ctx.font='bold 13px "Segoe UI",sans-serif';ctx.fillStyle='#93c5fd';ctx.textAlign='center';
  ctx.fillText('🔄 Pivot Joint',150,35);
  // Neck rotation demo
  let headAngle=Math.sin(t*0.02)*0.6;
  ctx.save();ctx.translate(150,130);
  // Spine (fixed)
  ctx.beginPath();ctx.moveTo(0,20);ctx.lineTo(0,80);ctx.strokeStyle='#bfdbfe';ctx.lineWidth=8;ctx.lineCap='round';ctx.stroke();
  // Pivot point
  ctx.beginPath();ctx.arc(0,15,8,0,Math.PI*2);ctx.fillStyle='#3b82f6';ctx.fill();
  // Head rotating
  ctx.rotate(headAngle);
  ctx.beginPath();ctx.ellipse(0,-20,25,30,0,0,Math.PI*2);ctx.fillStyle='#60a5fa44';ctx.fill();ctx.strokeStyle='#60a5fa';ctx.lineWidth=2;ctx.stroke();
  ctx.font='20px serif';ctx.textAlign='center';ctx.fillText('😊',0,-18);
  ctx.restore();
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#93c5fd';ctx.textAlign='center';
  ctx.fillText('Neck turns left ↔ right',150,225);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#60a5fa';
  ctx.fillText('One bone rotates around another',150,242);

  // RIGHT - Gliding Joint
  ctx.fillStyle='rgba(23,37,84,0.5)';ctx.beginPath();ctx.roundRect(315,10,270,260,14);ctx.fill();
  ctx.strokeStyle='#8b5cf644';ctx.lineWidth=1;ctx.stroke();
  ctx.font='bold 13px "Segoe UI",sans-serif';ctx.fillStyle='#c4b5fd';ctx.textAlign='center';
  ctx.fillText('↔️ Gliding Joint',450,35);
  // Two flat bones sliding
  let slide=Math.sin(t*0.025)*20;
  ctx.fillStyle='#7c3aed44';ctx.beginPath();ctx.roundRect(400,100,100,30,6);ctx.fill();ctx.strokeStyle='#a78bfa';ctx.lineWidth=2;ctx.stroke();
  ctx.fillStyle='#6d28d944';ctx.beginPath();ctx.roundRect(400+slide,135,100,30,6);ctx.fill();ctx.strokeStyle='#c4b5fd';ctx.lineWidth=2;ctx.stroke();
  // Arrows
  ctx.beginPath();ctx.moveTo(420+slide,150);ctx.lineTo(480+slide,150);
  ctx.strokeStyle='#c4b5fd55';ctx.lineWidth=1;ctx.setLineDash([3,3]);ctx.stroke();ctx.setLineDash([]);
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#c4b5fd';ctx.textAlign='center';
  ctx.fillText('Wrist & Ankle bones',450,225);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#a78bfa';
  ctx.fillText('Flat bones slide over each other',450,242);

  // VS
  ctx.font='bold 14px "Segoe UI",sans-serif';ctx.fillStyle='#64748b';ctx.textAlign='center';ctx.fillText('VS',300,140);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "muscle_contraction":
        components.html("""
<div style="background:linear-gradient(135deg,#4c0519,#881337);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fecdd3;margin:0 0 16px;font-size:18px;">Muscle Contraction — Pull, Never Push!</h4>
<canvas id="c" width="600" height="280"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,280);
  let flex=Math.sin(t*0.02)*0.8;
  // Upper arm bone
  ctx.beginPath();ctx.moveTo(200,60);ctx.lineTo(200,140);
  ctx.strokeStyle='#fef3c7';ctx.lineWidth=12;ctx.lineCap='round';ctx.stroke();
  // Elbow pivot
  ctx.beginPath();ctx.arc(200,145,8,0,Math.PI*2);ctx.fillStyle='#f59e0b';ctx.fill();
  // Forearm swinging
  let fAngle=flex*0.7+0.3;
  let fEndX=200+Math.sin(fAngle)*100;
  let fEndY=145+Math.cos(fAngle)*100;
  ctx.beginPath();ctx.moveTo(200,145);ctx.lineTo(fEndX,fEndY);
  ctx.strokeStyle='#fde68a';ctx.lineWidth=10;ctx.lineCap='round';ctx.stroke();
  // Bicep (contracts when bending)
  let bicepBulge=15+Math.max(0,-flex)*12;
  ctx.beginPath();ctx.ellipse(185,110,bicepBulge,30,0,0,Math.PI*2);
  ctx.fillStyle=flex<0?'#ef444488':'#ef444444';ctx.fill();
  ctx.strokeStyle='#f87171';ctx.lineWidth=2;ctx.stroke();
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#fecdd3';ctx.textAlign='center';
  ctx.fillText('BICEP',185,115);
  ctx.fillText(flex<0?'(Contracting!)':'(Relaxed)',185,128);
  // Tricep (opposite)
  let tricepBulge=15+Math.max(0,flex)*12;
  ctx.beginPath();ctx.ellipse(215,110,tricepBulge,28,0,0,Math.PI*2);
  ctx.fillStyle=flex>0?'#3b82f688':'#3b82f644';ctx.fill();
  ctx.strokeStyle='#60a5fa';ctx.lineWidth=2;ctx.stroke();
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#bfdbfe';
  ctx.fillText('TRICEP',215,115);
  ctx.fillText(flex>0?'(Contracting!)':'(Relaxed)',215,128);
  // Info on right
  ctx.font='13px "Segoe UI",sans-serif';ctx.fillStyle='#fecdd3';ctx.textAlign='left';
  ctx.fillText('Key Facts:',380,70);
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#fda4af';
  ctx.fillText('• Muscles can only PULL (contract)',380,95);
  ctx.fillText('• They work in PAIRS (antagonistic)',380,115);
  ctx.fillText('• Bicep bends arm, Tricep straightens',380,135);
  ctx.fillText('• Attached to bones by TENDONS',380,155);
  ctx.font='bold 11px "Segoe UI",sans-serif';ctx.fillStyle='#fb7185';
  ctx.fillText('Watch the pair work together! →',380,185);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "muscle_types":
        components.html("""
<div style="background:linear-gradient(135deg,#3b0764,#581c87);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#e9d5ff;margin:0 0 16px;font-size:18px;">3 Types of Muscles</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#c084fc;font-size:11px;margin:8px 0 0;">Click to compare</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const types=[
  {x:120,y:110,icon:'💪',name:'Skeletal (Striped)',ctrl:'Voluntary — YOU control',where:'Arms, legs, face',fact:'Can get tired! 640+ in body',color:'#f472b6'},
  {x:300,y:110,icon:'🫁',name:'Smooth',ctrl:'Involuntary — automatic',where:'Stomach, intestines, blood vessels',fact:'Works without thinking! Never tires easily',color:'#a78bfa'},
  {x:480,y:110,icon:'❤️',name:'Cardiac (Heart)',ctrl:'Involuntary — automatic',where:'Only in the heart',fact:'Beats 100,000 times/day! Never stops',color:'#f87171'}
];
c.addEventListener('click',e=>{
  const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;
  let prev=selected;selected=-1;
  types.forEach((tp,i)=>{if(Math.hypot(mx-tp.x,my-tp.y)<40)selected=i;});
  if(selected===prev)selected=-1;
});
function draw(){
  ctx.clearRect(0,0,600,280);
  types.forEach((tp,i)=>{
    let active=selected===i;let bounce=Math.sin(t*0.03+i*1.3)*4;let s=active?1.15:1;
    // Pulsing for heart
    let heartPulse=i===2?Math.abs(Math.sin(t*0.06))*5:0;
    ctx.save();ctx.translate(tp.x,tp.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=tp.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.arc(0,0,36+heartPulse,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,38);g.addColorStop(0,tp.color+'44');g.addColorStop(1,'#3b0764');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?tp.color:'rgba(255,255,255,0.12)';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='28px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(tp.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';ctx.fillStyle=active?tp.color:'#e9d5ff';ctx.textAlign='center';
    ctx.fillText(tp.name,tp.x,tp.y+bounce+54);
  });
  if(selected>=0){let tp=types[selected];
    ctx.fillStyle='rgba(59,7,100,0.95)';ctx.beginPath();ctx.roundRect(50,200,500,70,12);ctx.fill();
    ctx.strokeStyle=tp.color+'55';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='bold 13px "Segoe UI",sans-serif';ctx.fillStyle=tp.color;ctx.textAlign='center';ctx.fillText(tp.icon+' '+tp.name,300,222);
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#f5f3ff';ctx.fillText('Control: '+tp.ctrl,300,240);
    ctx.fillStyle='#e9d5ff';ctx.fillText('Found: '+tp.where+' | '+tp.fact,300,258);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=360)
        return True

    elif anim_type == "body_system_overview":
        components.html("""
<div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#c4b5fd;margin:0 0 16px;font-size:18px;">How It All Works Together — The Movement System</h4>
<canvas id="c" width="600" height="260"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;
c.width=600*dpr;c.height=260*dpr;c.style.width='600px';c.style.height='260px';ctx.scale(dpr,dpr);
let t=0;
const parts=[
  {x:500,icon:'🧠',label:'Brain Signal',desc:'Sends electrical impulse',color:'#818cf8'},
  {x:380,icon:'⚡',label:'Nerve',desc:'Carries message to muscle',color:'#fbbf24'},
  {x:260,icon:'💪',label:'Muscle',desc:'Contracts (shortens)',color:'#f472b6'},
  {x:140,icon:'🦴',label:'Bone',desc:'Gets pulled by muscle',color:'#e2e8f0'},
  {x:30,icon:'🏃',label:'Movement!',desc:'Body part moves',color:'#34d399'}
];
function draw(){
  ctx.clearRect(0,0,600,260);
  // Signal pulse traveling RTL
  let pulseX=540-((t*2)%580);
  ctx.beginPath();ctx.arc(pulseX,100,4,0,Math.PI*2);
  ctx.fillStyle='#818cf8';ctx.fill();
  ctx.shadowColor='#818cf8';ctx.shadowBlur=10;
  ctx.beginPath();ctx.arc(pulseX,100,2,0,Math.PI*2);ctx.fill();
  ctx.shadowBlur=0;
  // Connection line
  ctx.beginPath();ctx.moveTo(530,100);ctx.lineTo(60,100);
  ctx.strokeStyle='#4338ca33';ctx.lineWidth=3;ctx.stroke();
  parts.forEach((p,i)=>{
    let progress=(t*0.01)%5;
    let active=Math.floor(progress)===i;
    let bounce=Math.sin(t*0.03+i)*3;
    ctx.save();ctx.translate(p.x+30,100+bounce);
    if(active){ctx.shadowColor=p.color;ctx.shadowBlur=14;}
    ctx.beginPath();ctx.arc(0,0,28,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-3,2,0,0,28);g.addColorStop(0,p.color+'55');g.addColorStop(1,'#1e1b4b');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?p.color:p.color+'44';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='20px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(p.icon,0,0);
    ctx.restore();
    // Arrow RTL
    if(i<4){let ax=p.x-5;ctx.beginPath();ctx.moveTo(ax,100);ctx.lineTo(ax-15,100);ctx.strokeStyle=p.color+'66';ctx.lineWidth=2;ctx.stroke();
      ctx.beginPath();ctx.moveTo(ax-11,96);ctx.lineTo(ax-17,100);ctx.lineTo(ax-11,104);ctx.fillStyle=p.color;ctx.fill();}
    ctx.font='bold 10px "Segoe UI",sans-serif';ctx.fillStyle=p.color;ctx.textAlign='center';
    ctx.fillText(p.label,p.x+30,145+bounce);
    ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle='#a5b4fc';
    ctx.fillText(p.desc,p.x+30,159+bounce);
  });
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#7c3aed';ctx.textAlign='center';
  ctx.fillText('← Signal flows from brain to movement in milliseconds!',300,220);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#6366f1';
  ctx.fillText('Skeleton + Joints + Muscles + Nerves = The Movement System',300,240);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=330)
        return True

    elif anim_type == "nervous_system_parts":
        components.html("""
<div style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#c4b5fd;margin:0 0 16px;font-size:18px;">The Nervous System — 3 Key Parts</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#a5b4fc;font-size:11px;margin:8px 0 0;">Click each part to explore</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const parts=[
  {x:150,y:80,icon:'🧠',name:'Brain',desc:'Control centre — processes all information and sends instructions',role:'The Boss',color:'#a78bfa'},
  {x:150,y:170,icon:'🦴',name:'Spinal Cord',desc:'Information highway connecting brain to body, inside the backbone',role:'The Highway',color:'#34d399'},
  {x:420,y:130,icon:'⚡',name:'Nerves',desc:'Network of messengers carrying signals to/from every body part',role:'The Messengers',color:'#fbbf24'}
];
c.addEventListener('click',e=>{const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;let prev=selected;selected=-1;parts.forEach((p,i)=>{if(Math.hypot(mx-p.x,my-p.y)<40)selected=i;});if(selected===prev)selected=-1;});
function draw(){
  ctx.clearRect(0,0,600,280);
  // Signal pulses traveling
  for(let i=0;i<6;i++){let px=150+((t*1.5+i*100)%300),py=130+Math.sin(t*0.03+i)*20;ctx.beginPath();ctx.arc(px,py,2.5,0,Math.PI*2);ctx.fillStyle='#a78bfa55';ctx.fill();}
  // Connection lines
  ctx.beginPath();ctx.moveTo(150,110);ctx.lineTo(150,145);ctx.strokeStyle='#34d39966';ctx.lineWidth=3;ctx.stroke();
  ctx.beginPath();ctx.moveTo(170,170);ctx.lineTo(390,135);ctx.strokeStyle='#fbbf2444';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);
  ctx.beginPath();ctx.moveTo(170,80);ctx.lineTo(390,125);ctx.strokeStyle='#fbbf2444';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);
  parts.forEach((p,i)=>{
    let active=selected===i;let bounce=Math.sin(t*0.03+i)*4;let s=active?1.15:1;
    ctx.save();ctx.translate(p.x,p.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=p.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.arc(0,0,36,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,36);g.addColorStop(0,p.color+'44');g.addColorStop(1,'#0f172a');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?p.color:'rgba(255,255,255,0.1)';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='28px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(p.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';ctx.fillStyle=active?p.color:'#e2e8f0';ctx.textAlign='center';
    ctx.fillText(p.name+' — '+p.role,p.x,p.y+bounce+52);
  });
  if(selected>=0){let p=parts[selected];
    ctx.fillStyle='rgba(15,23,42,0.95)';ctx.beginPath();ctx.roundRect(50,235,500,35,8);ctx.fill();
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#f1f5f9';ctx.textAlign='center';ctx.fillText(p.icon+' '+p.desc,300,257);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=360)
        return True

    elif anim_type == "brain_parts":
        components.html("""
<div style="background:linear-gradient(135deg,#3b0764,#581c87);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#e9d5ff;margin:0 0 16px;font-size:18px;">Three Parts of the Brain</h4>
<canvas id="c" width="600" height="280"></canvas>
<p style="text-align:center;color:#c084fc;font-size:11px;margin:8px 0 0;">Click each brain region</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=280*dpr;c.style.width='600px';c.style.height='280px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const parts=[
  {x:200,y:80,r:55,name:'Cerebrum',desc:'Largest part — controls thinking, learning, memory, senses',icon:'🧩',color:'#a78bfa'},
  {x:220,y:175,r:30,name:'Cerebellum',desc:'Below cerebrum — controls balance and muscle movement',icon:'⚖️',color:'#f472b6'},
  {x:280,y:210,r:22,name:'Medulla',desc:'Stem-shaped — controls breathing, heartbeat, swallowing',icon:'🫁',color:'#34d399'}
];
c.addEventListener('click',e=>{const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;let prev=selected;selected=-1;parts.forEach((p,i)=>{if(Math.hypot(mx-p.x,my-p.y)<p.r)selected=i;});if(selected===prev)selected=-1;});
function draw(){
  ctx.clearRect(0,0,600,280);
  // Brain outline
  ctx.beginPath();ctx.ellipse(220,140,90,110,0,0,Math.PI*2);ctx.fillStyle='#4c1d95';ctx.fill();ctx.strokeStyle='#7c3aed';ctx.lineWidth=2;ctx.stroke();
  // Wrinkle lines
  for(let i=0;i<5;i++){ctx.beginPath();ctx.arc(180+i*15,70+i*10,20+i*5,0.3,2.5);ctx.strokeStyle='#6d28d944';ctx.lineWidth=1;ctx.stroke();}
  parts.forEach((p,i)=>{
    let active=selected===i;let pulse=active?Math.sin(t*0.06)*4:0;
    ctx.save();if(active){ctx.shadowColor=p.color;ctx.shadowBlur=15;}
    ctx.beginPath();ctx.arc(p.x,p.y,p.r+pulse,0,Math.PI*2);
    ctx.fillStyle=active?p.color+'44':'transparent';ctx.fill();
    ctx.strokeStyle=active?p.color:p.color+'66';ctx.lineWidth=active?3:1.5;ctx.stroke();
    ctx.shadowBlur=0;ctx.restore();
  });
  // Labels on right
  ctx.font='11px "Segoe UI",sans-serif';ctx.textAlign='left';
  parts.forEach((p,i)=>{
    let active=selected===i;
    ctx.fillStyle=active?p.color:'#d8b4fe';
    ctx.fillText(p.icon+' '+p.name,380,70+i*40);
    // pointer line
    ctx.beginPath();ctx.moveTo(p.x+p.r+5,p.y);ctx.lineTo(375,62+i*40);ctx.strokeStyle=p.color+'44';ctx.lineWidth=1;ctx.setLineDash([2,3]);ctx.stroke();ctx.setLineDash([]);
  });
  if(selected>=0){let p=parts[selected];
    ctx.fillStyle='rgba(59,7,100,0.95)';ctx.beginPath();ctx.roundRect(50,250,500,25,6);ctx.fill();
    ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#f5f3ff';ctx.textAlign='center';ctx.fillText(p.icon+' '+p.name+': '+p.desc,300,266);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=350)
        return True

    elif anim_type == "spinal_cord_pathway":
        components.html("""
<div style="background:linear-gradient(135deg,#064e3b,#065f46);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#6ee7b7;margin:0 0 16px;font-size:18px;">Spinal Cord — The Information Highway</h4>
<canvas id="c" width="600" height="240"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=240*dpr;c.style.width='600px';c.style.height='240px';ctx.scale(dpr,dpr);
let t=0;
function draw(){
  ctx.clearRect(0,0,600,240);
  // Brain at top
  ctx.beginPath();ctx.ellipse(300,35,30,25,0,0,Math.PI*2);ctx.fillStyle='#a78bfa44';ctx.fill();ctx.strokeStyle='#a78bfa';ctx.lineWidth=2;ctx.stroke();
  ctx.font='20px serif';ctx.textAlign='center';ctx.fillText('🧠',300,42);
  // Spinal cord (vertical)
  ctx.beginPath();ctx.moveTo(300,60);ctx.lineTo(300,200);ctx.strokeStyle='#34d399';ctx.lineWidth=6;ctx.lineCap='round';ctx.stroke();
  // Vertebrae
  for(let i=0;i<7;i++){let vy=70+i*20;ctx.beginPath();ctx.ellipse(300,vy,15,6,0,0,Math.PI*2);ctx.strokeStyle='#6ee7b744';ctx.lineWidth=1;ctx.stroke();}
  // Nerves branching out
  for(let i=0;i<5;i++){
    let ny=80+i*28;
    ctx.beginPath();ctx.moveTo(300,ny);ctx.lineTo(380+i*10,ny+10);ctx.moveTo(300,ny);ctx.lineTo(220-i*10,ny+10);
    ctx.strokeStyle='#fbbf2488';ctx.lineWidth=1.5;ctx.stroke();
  }
  // Signals traveling up and down
  for(let i=0;i<4;i++){
    let sy=60+((t*1.5+i*50)%150);// going down
    ctx.beginPath();ctx.arc(295,sy,3,0,Math.PI*2);ctx.fillStyle='#34d399';ctx.fill();
    let sy2=200-((t*1.5+i*50)%150);// going up
    ctx.beginPath();ctx.arc(305,sy2,3,0,Math.PI*2);ctx.fillStyle='#fbbf24';ctx.fill();
  }
  // Labels
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#6ee7b7';ctx.textAlign='left';
  ctx.fillText('🧠 Brain (Control Centre)',340,40);
  ctx.fillText('🦴 Vertebral Column (Protection)',340,120);
  ctx.fillText('⚡ Nerves branch out to body',340,160);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#34d399';ctx.textAlign='center';
  ctx.fillText('↓ Motor signals (brain → body)',260,225);
  ctx.fillStyle='#fbbf24';ctx.fillText('↑ Sensory signals (body → brain)',420,225);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=310)
        return True

    elif anim_type == "nerve_types":
        components.html("""
<div style="background:linear-gradient(135deg,#172554,#1e3a5f);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#bfdbfe;margin:0 0 16px;font-size:18px;">Three Types of Nerves</h4>
<canvas id="c" width="600" height="260"></canvas>
<p style="text-align:center;color:#93c5fd;font-size:11px;margin:8px 0 0;">Click to learn about each type</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=260*dpr;c.style.width='600px';c.style.height='260px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const types=[
  {x:120,y:100,icon:'👁️',name:'Sensory',dir:'Sense Organs → Brain',desc:'Carry messages FROM senses TO brain (see, hear, smell, taste, feel)',color:'#60a5fa'},
  {x:300,y:100,icon:'💪',name:'Motor',dir:'Brain → Muscles',desc:'Carry instructions FROM brain TO muscles and glands (move, act)',color:'#f472b6'},
  {x:480,y:100,icon:'🔄',name:'Mixed',dir:'Both Directions',desc:'Carry messages BOTH ways — detect AND respond through same nerve',color:'#a78bfa'}
];
c.addEventListener('click',e=>{const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;let prev=selected;selected=-1;types.forEach((tp,i)=>{if(Math.hypot(mx-tp.x,my-tp.y)<38)selected=i;});if(selected===prev)selected=-1;});
function draw(){
  ctx.clearRect(0,0,600,260);
  types.forEach((tp,i)=>{
    let active=selected===i;let bounce=Math.sin(t*0.03+i*1.2)*4;let s=active?1.15:1;
    ctx.save();ctx.translate(tp.x,tp.y+bounce);ctx.scale(s,s);
    if(active){ctx.shadowColor=tp.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.arc(0,0,35,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-5,3,0,0,35);g.addColorStop(0,tp.color+'44');g.addColorStop(1,'#172554');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?tp.color:'rgba(255,255,255,0.1)';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='26px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(tp.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 11px "Segoe UI",sans-serif';ctx.fillStyle=active?tp.color:'#bfdbfe';ctx.textAlign='center';
    ctx.fillText(tp.name+' Nerves',tp.x,tp.y+bounce+50);
    ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle='#93c5fd';ctx.fillText(tp.dir,tp.x,tp.y+bounce+63);
  });
  if(selected>=0){let tp=types[selected];
    ctx.fillStyle='rgba(23,37,84,0.95)';ctx.beginPath();ctx.roundRect(50,200,500,45,10);ctx.fill();
    ctx.strokeStyle=tp.color+'44';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#f1f5f9';ctx.textAlign='center';ctx.fillText(tp.icon+' '+tp.name+': '+tp.desc,300,227);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=330)
        return True

    elif anim_type == "reflex_action":
        components.html("""
<div style="background:linear-gradient(135deg,#7c2d12,#431407);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#fed7aa;margin:0 0 16px;font-size:18px;">Reflex Action — Faster Than Thought!</h4>
<canvas id="c" width="600" height="260"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=260*dpr;c.style.width='600px';c.style.height='260px';ctx.scale(dpr,dpr);
let t=0;
const steps=[
  {x:80,y:130,icon:'🔥',label:'Hot Object',color:'#ef4444'},
  {x:200,y:130,icon:'🖐️',label:'Hand touches',color:'#f97316'},
  {x:320,y:130,icon:'⚡',label:'Sensory nerve',color:'#fbbf24'},
  {x:440,y:130,icon:'🦴',label:'Spinal cord',color:'#34d399'},
  {x:440,y:50,icon:'🧠',label:'Brain (skipped!)',color:'#64748b'},
  {x:560,y:130,icon:'💪',label:'Hand pulls back!',color:'#60a5fa'}
];
function draw(){
  ctx.clearRect(0,0,600,260);
  // Main pathway arrows (LTR process)
  let progress=(t*0.015)%6;
  for(let i=0;i<5;i++){
    if(i===3){// Skip brain path
      ctx.setLineDash([3,5]);ctx.beginPath();ctx.moveTo(440,105);ctx.lineTo(440,70);
      ctx.strokeStyle='#64748b44';ctx.lineWidth=1.5;ctx.stroke();ctx.setLineDash([]);
      // X mark
      ctx.font='14px sans-serif';ctx.fillStyle='#ef4444';ctx.textAlign='center';ctx.fillText('✗',440,85);
      continue;
    }
    let fromIdx=i<4?i:3;let toIdx=i<3?i+1:(i===4?5:i+1);
    if(toIdx>5)continue;
    ctx.beginPath();ctx.moveTo(steps[fromIdx].x+30,steps[fromIdx].y);ctx.lineTo(steps[toIdx].x-30,steps[toIdx].y);
    ctx.strokeStyle=steps[fromIdx].color+'66';ctx.lineWidth=2;ctx.stroke();
    let ax=steps[toIdx].x-32;ctx.beginPath();ctx.moveTo(ax-6,steps[toIdx].y-4);ctx.lineTo(ax,steps[toIdx].y);ctx.lineTo(ax-6,steps[toIdx].y+4);ctx.fillStyle=steps[fromIdx].color;ctx.fill();
  }
  // Arrow from spinal cord to response
  ctx.beginPath();ctx.moveTo(465,130);ctx.lineTo(530,130);ctx.strokeStyle='#34d39966';ctx.lineWidth=2;ctx.stroke();
  // Signal pulse
  let pulseIdx=Math.floor(progress);
  steps.forEach((s,i)=>{
    if(i===4)return;// skip brain display in main loop
    let active=pulseIdx===i;let bounce=Math.sin(t*0.03+i)*3;
    ctx.save();ctx.translate(s.x,s.y+bounce);
    if(active){ctx.shadowColor=s.color;ctx.shadowBlur=14;}
    ctx.beginPath();ctx.arc(0,0,25,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-3,2,0,0,25);g.addColorStop(0,s.color+'55');g.addColorStop(1,'#431407');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?s.color:s.color+'44';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='18px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(s.icon,0,0);
    ctx.restore();
    ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle=s.color;ctx.textAlign='center';ctx.fillText(s.label,s.x,s.y+bounce+35);
  });
  // Brain (greyed out with X)
  ctx.globalAlpha=0.4;ctx.font='20px serif';ctx.textAlign='center';ctx.fillText('🧠',440,55);ctx.globalAlpha=1;
  ctx.font='8px "Segoe UI",sans-serif';ctx.fillStyle='#64748b';ctx.fillText('Brain skipped',440,75);
  ctx.fillText('(too slow!)',440,85);
  // Info
  ctx.font='11px "Segoe UI",sans-serif';ctx.fillStyle='#fdba74';ctx.textAlign='center';
  ctx.fillText('Reflex path: Stimulus → Sensory nerve → Spinal cord → Motor nerve → Response (0.03 sec!)',300,230);
  ctx.font='10px "Segoe UI",sans-serif';ctx.fillStyle='#f97316';
  ctx.fillText('Signal goes to spinal cord directly — brain is NOT involved → much faster!',300,248);
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=330)
        return True

    elif anim_type == "five_senses":
        components.html("""
<div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:#c4b5fd;margin:0 0 16px;font-size:18px;">Five Sense Organs</h4>
<canvas id="c" width="600" height="260"></canvas>
<p style="text-align:center;color:#a5b4fc;font-size:11px;margin:8px 0 0;">Click to explore each sense</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=260*dpr;c.style.width='600px';c.style.height='260px';ctx.scale(dpr,dpr);
let t=0,selected=-1;
const senses=[
  {x:60,y:100,icon:'👁️',name:'Eyes',sense:'Vision',desc:'Detect light, form images on retina',color:'#60a5fa'},
  {x:180,y:100,icon:'👂',name:'Ears',sense:'Hearing',desc:'Convert sound vibrations to nerve signals',color:'#34d399'},
  {x:300,y:100,icon:'👃',name:'Nose',sense:'Smell',desc:'Detect odour molecules, filter air',color:'#fbbf24'},
  {x:420,y:100,icon:'👅',name:'Tongue',sense:'Taste',desc:'Taste buds detect sweet, sour, salty, bitter',color:'#f472b6'},
  {x:540,y:100,icon:'🖐️',name:'Skin',sense:'Touch',desc:'Feel heat, cold, pressure, pain',color:'#a78bfa'}
];
c.addEventListener('click',e=>{const r=c.getBoundingClientRect();const mx=e.clientX-r.left,my=e.clientY-r.top;let prev=selected;selected=-1;senses.forEach((s,i)=>{if(Math.hypot(mx-s.x,my-s.y)<36)selected=i;});if(selected===prev)selected=-1;});
function draw(){
  ctx.clearRect(0,0,600,260);
  senses.forEach((s,i)=>{
    let active=selected===i;let bounce=Math.sin(t*0.03+i*1.1)*4;let sc=active?1.15:1;
    ctx.save();ctx.translate(s.x,s.y+bounce);ctx.scale(sc,sc);
    if(active){ctx.shadowColor=s.color;ctx.shadowBlur=18;}
    ctx.beginPath();ctx.arc(0,0,33,0,Math.PI*2);
    let g=ctx.createRadialGradient(0,-4,2,0,0,33);g.addColorStop(0,s.color+'44');g.addColorStop(1,'#1e1b4b');
    ctx.fillStyle=g;ctx.fill();ctx.strokeStyle=active?s.color:'rgba(255,255,255,0.1)';ctx.lineWidth=active?2.5:1;ctx.stroke();
    ctx.shadowBlur=0;ctx.font='26px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(s.icon,0,0);
    ctx.restore();
    ctx.font=(active?'bold ':'')+' 10px "Segoe UI",sans-serif';ctx.fillStyle=active?s.color:'#c4b5fd';ctx.textAlign='center';
    ctx.fillText(s.name,s.x,s.y+bounce+48);
    ctx.font='9px "Segoe UI",sans-serif';ctx.fillStyle='#a5b4fc';ctx.fillText(s.sense,s.x,s.y+bounce+61);
  });
  if(selected>=0){let s=senses[selected];
    ctx.fillStyle='rgba(30,27,75,0.95)';ctx.beginPath();ctx.roundRect(60,200,480,40,10);ctx.fill();
    ctx.strokeStyle=s.color+'55';ctx.lineWidth=1.5;ctx.stroke();
    ctx.font='12px "Segoe UI",sans-serif';ctx.fillStyle='#f1f5f9';ctx.textAlign='center';ctx.fillText(s.icon+' '+s.name+' ('+s.sense+'): '+s.desc,300,224);
  }
  t++;requestAnimationFrame(draw);
}
draw();
</script></div>
        """, height=320)
        return True

    elif anim_type in ("eye_structure", "ear_structure", "nose_tongue_skin", "signal_pathway", "neuron_structure"):
        # Simplified professional display for remaining types
        descs = {
            "eye_structure": ("👁️ Eye Structure", "Light → Cornea → Pupil → Lens → Retina → Optic Nerve → Brain", "#60a5fa"),
            "ear_structure": ("👂 Ear Structure", "Sound → Pinna → Ear Canal → Eardrum → 3 Tiny Bones → Cochlea → Auditory Nerve → Brain", "#34d399"),
            "nose_tongue_skin": ("👃👅🖐️ Smell, Taste & Touch", "Nose: odour molecules → nasal cells → brain | Tongue: taste buds → nerve → brain | Skin: pressure/heat → nerve → brain", "#fbbf24"),
            "signal_pathway": ("⚡ Signal Pathway", "Stimulus → Sense Organ → Sensory Nerve → Spinal Cord → Brain → Motor Nerve → Muscle → Response", "#a78bfa"),
            "neuron_structure": ("🔬 Neuron", "Dendrites (receive) → Cell Body (process) → Axon (transmit) → Next Neuron | Speed: up to 120 m/s!", "#f472b6")
        }
        title, desc, color = descs[anim_type]
        components.html(f"""
<div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;padding:24px;font-family:'Segoe UI',system-ui,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
<h4 style="text-align:center;color:{color};margin:0 0 16px;font-size:18px;">{title}</h4>
<canvas id="c" width="600" height="180"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const dpr=window.devicePixelRatio||1;c.width=600*dpr;c.height=180*dpr;c.style.width='600px';c.style.height='180px';ctx.scale(dpr,dpr);
let t=0;
const steps="{desc}".split(/→|\\|/);
function draw(){{
  ctx.clearRect(0,0,600,180);
  let cols=Math.min(steps.length,6);let w=560/cols;
  let progress=(t*0.012)%steps.length;
  steps.forEach((s,i)=>{{
    let row=Math.floor(i/6),col=i%6;
    let x=30+col*w+w/2,y=50+row*70;
    let active=Math.floor(progress)===i;
    ctx.beginPath();ctx.roundRect(x-w/2+5,y-20,w-10,40,8);
    ctx.fillStyle=active?'{color}33':'rgba(30,41,59,0.8)';ctx.fill();
    ctx.strokeStyle=active?'{color}':'{color}44';ctx.lineWidth=active?2:1;ctx.stroke();
    ctx.font=(active?'bold ':'')+'10px "Segoe UI",sans-serif';ctx.fillStyle=active?'#f1f5f9':'#94a3b8';ctx.textAlign='center';
    ctx.fillText(s.trim(),x,y+4);
    if(i<steps.length-1&&col<5){{
      ctx.beginPath();ctx.moveTo(x+w/2-8,y);ctx.lineTo(x+w/2,y);ctx.strokeStyle='{color}66';ctx.lineWidth=1.5;ctx.stroke();
    }}
  }});
  // Pulse dot
  let pulseCol=Math.floor(progress)%6,pulseRow=Math.floor(Math.floor(progress)/6);
  let px=30+pulseCol*w+w/2,py=50+pulseRow*70;
  ctx.beginPath();ctx.arc(px,py-25,4,0,Math.PI*2);ctx.fillStyle='{color}';ctx.fill();
  t++;requestAnimationFrame(draw);
}}
draw();
</script></div>
        """, height=250)
        return True

    return False



def render_animation(animation_config):
    """Render animations using interactive HTML5 Canvas."""
    anim_type = animation_config.get("type", "")
    if render_interactive_animation(anim_type):
        return
    # Fallback: show description if animation type not found
    desc = animation_config.get("description", "")
    if desc:
        st.info(f"🎬 {desc}")

# ─── Session State Initialization ─────────────────────────────────────────────

if "scene_index" not in st.session_state:
    st.session_state.scene_index = 0

if "chapter_started" not in st.session_state:
    st.session_state.chapter_started = False

if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = 1

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "student_name" not in st.session_state:
    st.session_state.student_name = "Explorer"

# ─── HOME PAGE ────────────────────────────────────────────────────────────────

if not st.session_state.chapter_started:

    st.title("🌟 WonderLearn")
    st.subheader("Learn Through Stories, Explore Through Adventures")

    col1, col2, col3 = st.columns(3)
    with col1:
        student_name = st.text_input("Student Name", value=st.session_state.student_name)
        st.session_state.student_name = student_name
    with col2:
        selected_class = st.selectbox("Class", ["Class 5"])
    with col3:
        subject = st.selectbox("Subject", ["General Science"])

    st.divider()

    # Load chapters
    chapters_file = Path("content/class5/science/chapters.json")
    if chapters_file.exists():
        with open(chapters_file) as f:
            chapters_data = json.load(f)
        chapters = chapters_data.get("chapters", [])
    else:
        chapters = []

    st.subheader(f"📚 {selected_class} — {subject}")

    for ch in chapters:
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.write(f"**Chapter {ch['id']}:** {ch['title']}")
            st.caption(f"🏆 Badge: {ch.get('badge', 'N/A')}")
        with col_btn:
            # Only enable chapters that have content
            chapter_path = Path(f"content/class5/science/chapter{ch['id']}/scenes.json")
            if chapter_path.exists():
                if st.button(f"▶ Start", key=f"start_ch{ch['id']}"):
                    st.session_state.selected_chapter = ch['id']
                    st.session_state.chapter_started = True
                    st.session_state.scene_index = 0
                    st.rerun()
            else:
                st.button("🔒 Coming Soon", key=f"soon_ch{ch['id']}", disabled=True)

    # XP display
    if st.session_state.xp > 0:
        st.divider()
        st.metric("⭐ Total XP Earned", st.session_state.xp)


# ─── CHAPTER PLAYBACK ─────────────────────────────────────────────────────────

else:
    # Load chapter data
    ch_id = st.session_state.selected_chapter
    chapter_file = Path(f"content/class5/science/chapter{ch_id}/chapter.json")
    scenes_file = Path(f"content/class5/science/chapter{ch_id}/scenes.json")

    chapter_data = None
    scenes_data = None

    if chapter_file.exists():
        with open(chapter_file) as f:
            chapter_data = json.load(f)
    if scenes_file.exists():
        with open(scenes_file) as f:
            scenes_data = json.load(f)

    if chapter_data is None or scenes_data is None:
        st.warning("🚧 This adventure is under development and will be available soon.")
        if st.button("🏠 Return to Home"):
            st.session_state.chapter_started = False
            st.session_state.scene_index = 0
            st.rerun()
        st.stop()

    scene_count = len(scenes_data["scenes"])
    scene = scenes_data["scenes"][st.session_state.scene_index]

    # Progress bar
    st.progress((st.session_state.scene_index + 1) / scene_count)
    col_progress, col_xp = st.columns([3, 1])
    with col_progress:
        st.caption(f"📖 Chapter {ch_id}: {chapter_data.get('title', '')} — Scene {st.session_state.scene_index + 1} of {scene_count}")
    with col_xp:
        st.caption(f"⭐ XP: {st.session_state.xp}")

    st.divider()

    # ─── Scene Title + Character Avatar ─────────────────────────────────────────
    character_name = scene.get("character", "tara")
    character_display = character_name.title().replace("_", " ")
    character_file = Path(f"assets/characters/{character_name}.png")

    # Floating avatar next to title
    if character_file.exists():
        col_avatar, col_title = st.columns([0.08, 0.92])
        with col_avatar:
            st.image(str(character_file), width=48)
        with col_title:
            st.header(scene["title"])
            st.caption(f"🎭 {character_display}")
    else:
        st.header(scene["title"])
        st.caption(f"🎭 {character_display}")

    # ─── Narration ────────────────────────────────────────────────────────────
    st.write(scene["narration"])

    # TTS audio
    if scene.get("tts"):
        with st.expander("🔊 Listen to Narration"):
            render_audio_player(scene["narration"], scene["id"])

    # ─── Dialogue ─────────────────────────────────────────────────────────────
    if "dialogue" in scene:
        st.markdown(f"""
        <div class="dialogue-box">
            <span class="speaker">{scene['dialogue']['speaker']}:</span><br>
            {scene['dialogue']['text']}
        </div>
        """, unsafe_allow_html=True)

    # ─── Animation ────────────────────────────────────────────────────────────
    if "animation" in scene:
        render_animation(scene["animation"])

    # ─── Fun Fact ─────────────────────────────────────────────────────────────
    if "fun_fact" in scene:
        st.info(f"🌟 **Fun Fact:** {scene['fun_fact']}")

    # ─── Explore Hotspots ─────────────────────────────────────────────────────
    if "hotspots" in scene:
        st.write("")
        st.subheader("🔍 Explore & Learn")
        for hotspot in scene["hotspots"]:
            hotspot_title = hotspot.get('title', hotspot.get('name', 'Learn More'))
            hotspot_icon = hotspot.get('icon', '📌')
            with st.expander(f"{hotspot_icon} {hotspot_title}"):
                st.write(hotspot.get("description", hotspot.get("detail", "")))
                if "example" in hotspot:
                    st.success(f"💡 Example: {hotspot['example']}")

    # ─── Activity ─────────────────────────────────────────────────────────────
    if "activity" in scene:
        activity = scene["activity"]
        st.write("")
        st.subheader(f"🎮 {activity['title']}")
        st.write(activity["instructions"])

        # Matching Activity
        if activity["type"] == "matching":
            answers = {}
            options = activity["options"]

            for pair in activity["pairs"]:
                answers[pair["item"]] = st.selectbox(
                    f"{pair['icon']} {pair['item']}",
                    options=["— Select —"] + options,
                    key=f"match_{scene['id']}_{pair['item']}_ch{ch_id}"
                )

            if st.button("✅ Check Answers", key=f"check_match_{scene['id']}_ch{ch_id}"):
                correct = 0
                for pair in activity["pairs"]:
                    if answers.get(pair["item"]) == pair["match"]:
                        correct += 1
                        st.success(f"✅ {pair['item']} → {pair['match']}")
                    else:
                        st.error(f"❌ {pair['item']}: {pair.get('explanation', 'Try again!')}")
                st.write(f"**Score: {correct}/{len(activity['pairs'])}**")

        # Sorting Activity
        elif activity["type"] == "sorting":
            if "categories" in activity:
                for cat in activity["categories"]:
                    st.write(f"**{cat['name']}**")
                    for item in cat.get("items", []):
                        st.checkbox(f"{item}", key=f"sort_{scene['id']}_{item}_ch{ch_id}")

        # Labeling Activity
        elif activity["type"] == "labeling":
            if "items" in activity:
                for item in activity["items"]:
                    st.text_input(
                        f"{item.get('icon', '📝')} {item.get('hint', 'Label')}",
                        key=f"label_{scene['id']}_{item.get('id', '')}_ch{ch_id}"
                    )


    # ─── Challenge (True/False) ───────────────────────────────────────────────
    if "challenge" in scene:
        challenge = scene["challenge"]
        st.write("")
        st.subheader(f"🧠 {challenge.get('title', 'Challenge Time!')}")

        for q in challenge["questions"]:
            answer = st.radio(
                f"{q.get('id', '')}. {q['statement']}",
                options=["True", "False"],
                index=None,
                key=f"challenge_{scene['id']}_{q.get('id', '')}_ch{ch_id}",
                horizontal=True
            )

        if st.button("✅ Check Answers", key=f"check_challenge_{scene['id']}_ch{ch_id}"):
            correct = 0
            for q in challenge["questions"]:
                user_ans = st.session_state.get(f"challenge_{scene['id']}_{q.get('id', '')}_ch{ch_id}", "")
                correct_ans = str(q["answer"])
                if user_ans == correct_ans:
                    correct += 1
                    st.success(f"✅ {q['statement']} — Correct!")
                else:
                    st.error(f"❌ {q['statement']} — Answer: {correct_ans}. {q.get('explanation', '')}")
            st.write(f"**Score: {correct}/{len(challenge['questions'])}**")

    # ─── Quiz ─────────────────────────────────────────────────────────────────
    if "quiz" in scene:
        quiz = scene["quiz"]
        st.write("")
        st.subheader(f"📝 {quiz.get('title', 'Quiz Time!')}")

        for q in quiz["questions"]:
            st.radio(
                f"{q['id']}. {q['question']}",
                options=q["options"],
                index=None,
                key=f"quiz_{scene['id']}_{q['id']}_ch{ch_id}"
            )

        if st.button("✅ Submit Quiz", key=f"submit_quiz_{scene['id']}_ch{ch_id}"):
            correct = 0
            for q in quiz["questions"]:
                user_ans = st.session_state.get(f"quiz_{scene['id']}_{q['id']}_ch{ch_id}", "")
                if user_ans == q["answer"]:
                    correct += 1
                    st.success(f"✅ Q{q['id']}: Correct!")
                else:
                    st.error(f"❌ Q{q['id']}: The answer is: {q['answer']}. {q.get('explanation', '')}")
            total = len(quiz["questions"])
            st.write(f"**Score: {correct}/{total}**")
            if correct == total:
                st.balloons()

    # ─── Summary ──────────────────────────────────────────────────────────────
    if "summary" in scene or "summary_points" in scene:
        st.write("")
        st.subheader("📋 Chapter Summary")

        # Handle summary_points format (list of {icon, title, text})
        if "summary_points" in scene:
            for point in scene["summary_points"]:
                if isinstance(point, dict):
                    icon = point.get("icon", "📌")
                    title = point.get("title", "")
                    text = point.get("text", "")
                    st.write(f"{icon} **{title}:** {text}")
                else:
                    st.write(f"• {point}")

        # Handle summary format (dict with points list and key_terms)
        elif "summary" in scene:
            summary = scene["summary"]
            if isinstance(summary, dict):
                for point in summary.get("points", []):
                    st.write(f"• {point}")
                if "key_terms" in summary:
                    st.write("")
                    st.write("**Key Terms:**")
                    for term in summary["key_terms"]:
                        st.write(f"  **{term['term']}** — {term['definition']}")
            elif isinstance(summary, list):
                for point in summary:
                    st.write(f"• {point}")

    # ─── Badge Award ──────────────────────────────────────────────────────────
    if scene.get("scene_type") == "badge":
        st.write("")
        badge_data = scene.get("badge", {})
        if isinstance(badge_data, dict):
            badge_name = badge_data.get("name", chapter_data.get("badge", "Achievement"))
            badge_icon = badge_data.get("icon", "🏆")
            badge_desc = badge_data.get("description", "")
        else:
            badge_name = str(badge_data) if badge_data else chapter_data.get("badge", "Achievement")
            badge_icon = "🏆"
            badge_desc = ""
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #FEF3C7, #FDE68A); border-radius: 20px; margin: 20px 0;">
            <div style="font-size: 64px;">{badge_icon}</div>
            <h2 style="color: #92400E;">Congratulations, {st.session_state.student_name}!</h2>
            <h3 style="color: #B45309;">You earned the "{badge_name}" badge!</h3>
            <p style="color: #78350F;">{badge_desc}</p>
            <p style="color: #92400E; font-size: 14px;">You have completed Chapter {ch_id} successfully!</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

    # ─── XP Award ─────────────────────────────────────────────────────────────
    xp_key = f"xp_scene_{scene['id']}_ch{ch_id}"
    if xp_key not in st.session_state:
        xp_earned = scene.get("xp", 10)
        st.session_state.xp += xp_earned
        st.session_state[xp_key] = True
        st.toast(f"⭐ +{xp_earned} XP!")

    # ─── Navigation ───────────────────────────────────────────────────────────
    st.divider()
    col_prev, col_home, col_next = st.columns([1, 1, 1])

    with col_prev:
        if st.button("⬅ Previous", disabled=(st.session_state.scene_index == 0), key="nav_prev"):
            st.session_state.scene_index -= 1
            st.rerun()

    with col_home:
        if st.button("🏠 Home", key="nav_home"):
            st.session