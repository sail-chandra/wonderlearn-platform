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

    return False



def render_animation(animation_config):
    """Render animations — try interactive JS first, fall back to CSS."""
    anim_type = animation_config.get("type", "")

    # Try interactive animation first
    if render_interactive_animation(anim_type):
        return

    # Fall back to CSS animations for Chapter 1 and Chapter 3

    if anim_type == "germination_stages":
        st.markdown("""
        <div class="germination-anim">
            <div style="margin-bottom: 15px; font-weight: bold; color: #78350F;">🎬 Germination in Action</div>
            <div style="display: flex; justify-content: center; align-items: flex-end; gap: 30px; height: 150px;">
                <div style="text-align: center;">
                    <div class="seed-icon">🌰</div>
                    <div style="font-size: 12px; color: #78350F;">Seed</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite 0.5s;">💧</div>
                    <div style="font-size: 12px; color: #78350F;">+ Water</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite 1s;">💥</div>
                    <div style="font-size: 12px; color: #78350F;">Cracks</div>
                </div>
                <div style="text-align: center;">
                    <div class="root-anim">⬇️🌿</div>
                    <div style="font-size: 12px; color: #78350F;">Root Down</div>
                </div>
                <div style="text-align: center;">
                    <div class="shoot-anim">🌱</div>
                    <div style="font-size: 12px; color: #78350F;">Shoot Up!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "seed_dispersal":
        st.markdown("""
        <div class="animation-container">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #1E40AF;">🎬 Seeds on the Move!</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                <div style="text-align: center; padding: 15px;">
                    <div class="wind-seed">🌬️ 🪶</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Wind</strong><br>Floating away...</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div class="water-seed">🌊 🥥</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Water</strong><br>Floating downstream...</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 30px; animation: bounce 2s ease-in-out infinite;">🐕 🌿</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Animals</strong><br>Hitching a ride!</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div class="explode-seed">💥 🫛</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Explosion</strong><br>Pop! Scatter!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "seed_anatomy":
        st.markdown("""
        <div class="seed-anatomy">
            <div style="font-weight: bold; margin-bottom: 20px; color: #92400E;">🎬 Inside a Seed — Layers Revealed</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                <div class="seed-layer" style="animation-delay: 0s;">
                    <div class="seed-layer-icon">🛡️</div>
                    <div class="seed-layer-label">Seed Coat<br><small>(Outer protection)</small></div>
                </div>
                <div style="font-size: 24px; color: #92400E;">→</div>
                <div class="seed-layer" style="animation-delay: 0.5s;">
                    <div class="seed-layer-icon">🍽️</div>
                    <div class="seed-layer-label">Cotyledons<br><small>(Food storage)</small></div>
                </div>
                <div style="font-size: 24px; color: #92400E;">→</div>
                <div class="seed-layer" style="animation-delay: 1s;">
                    <div class="seed-layer-icon">🌱</div>
                    <div class="seed-layer-label">Embryo<br><small>(Baby plant)</small></div>
                </div>
            </div>
            <div style="margin-top: 15px; display: flex; justify-content: center; gap: 40px;">
                <div style="font-size: 13px; color: #78350F;">⬇️ Radicle (root)</div>
                <div style="font-size: 13px; color: #78350F;">⬆️ Plumule (shoot)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "stem_cutting":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #ECFDF5, #D1FAE5);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #065F46;">🎬 Growing a New Plant from a Stem Cutting</div>
            <div style="display: flex; justify-content: center; align-items: flex-end; gap: 25px; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 40px;">✂️🌿</div>
                    <div style="font-size: 12px; margin-top: 5px;">Cut a healthy stem</div>
                </div>
                <div style="font-size: 20px; color: #22C55E;">→</div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 2s infinite;">🪴</div>
                    <div style="font-size: 12px; margin-top: 5px;">Plant in moist soil</div>
                </div>
                <div style="font-size: 20px; color: #22C55E;">→</div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: sprout 3s ease-out infinite;">🌿⬇️</div>
                    <div style="font-size: 12px; margin-top: 5px;">Roots grow from base</div>
                </div>
                <div style="font-size: 20px; color: #22C55E;">→</div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite;">🌳</div>
                    <div style="font-size: 12px; margin-top: 5px;">New plant grows!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "agriculture_timeline":
        st.markdown("""
        <div style="margin: 20px 0;">
            <div style="font-weight: bold; text-align: center; margin-bottom: 15px; color: #92400E;">🎬 The Farming Journey</div>
            <div class="timeline-container">
                <div class="timeline-step"><div class="timeline-icon">🚜</div><div>Plough</div></div>
                <div class="timeline-step"><div class="timeline-icon">🧪</div><div>Manure</div></div>
                <div class="timeline-step"><div class="timeline-icon">🌱</div><div>Sow</div></div>
                <div class="timeline-step"><div class="timeline-icon">💧</div><div>Irrigate</div></div>
                <div class="timeline-step"><div class="timeline-icon">🐛</div><div>Protect</div></div>
                <div class="timeline-step"><div class="timeline-icon">🌾</div><div>Harvest</div></div>
                <div class="timeline-step"><div class="timeline-icon">🏪</div><div>Store</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "breathing_systems":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #EFF6FF, #DBEAFE);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #1E40AF;">🎬 How Animals Breathe</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite;">🫁</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Lungs</strong><br>Mammals, Birds<br>Nostrils → Windpipe → Lungs</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.5s;">🐟</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Gills</strong><br>Fish, Tadpoles<br>Water flows over gill filaments</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1s;">🐛</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Spiracles</strong><br>Insects<br>Tiny holes → Trachea tubes</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1.5s;">🪱</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Skin</strong><br>Earthworm<br>Moist skin absorbs O₂</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 2s;">🐋</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Blowhole</strong><br>Whales, Dolphins<br>Surface to breathe air</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "animal_movement":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #F0FDF4, #DCFCE7);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #166534;">🎬 Animals on the Move!</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                <div style="text-align: center; padding: 15px;">
                    <div class="wind-seed">🦅</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Flying</strong><br>Wings + Hollow bones<br>+ Streamlined body</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div class="water-seed">🐠</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Swimming</strong><br>Fins + Streamlined body<br>+ Tail propulsion</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite;">🦘</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Hopping</strong><br>Powerful back legs<br>Kangaroo, Frog</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.3s;">🐍</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Slithering</strong><br>Scales + Muscles<br>+ Flexible backbone</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.6s;">🦆</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Webbed Feet</strong><br>Skin between toes<br>Ducks, Frogs</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "habitat_types":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FEF3C7, #FDE68A);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #92400E;">🎬 Types of Animal Habitats</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 12px; background: #D1FAE5; border-radius: 12px; min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite;">🦁</div>
                    <div style="font-size: 12px; margin-top: 5px; font-weight: bold;">Terrestrial</div>
                    <div style="font-size: 11px; color: #065F46;">Land: forests,<br>deserts, grasslands</div>
                </div>
                <div style="text-align: center; padding: 12px; background: #DBEAFE; border-radius: 12px; min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.4s;">🐟</div>
                    <div style="font-size: 12px; margin-top: 5px; font-weight: bold;">Aquatic</div>
                    <div style="font-size: 11px; color: #1E40AF;">Water: oceans,<br>rivers, ponds</div>
                </div>
                <div style="text-align: center; padding: 12px; background: #E0E7FF; border-radius: 12px; min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.8s;">🐸</div>
                    <div style="font-size: 12px; margin-top: 5px; font-weight: bold;">Amphibious</div>
                    <div style="font-size: 11px; color: #3730A3;">Both land<br>& water</div>
                </div>
                <div style="text-align: center; padding: 12px; background: #D1FAE5; border-radius: 12px; min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1.2s;">🐒</div>
                    <div style="font-size: 12px; margin-top: 5px; font-weight: bold;">Arboreal</div>
                    <div style="font-size: 11px; color: #065F46;">Tree-tops:<br>monkeys, birds</div>
                </div>
                <div style="text-align: center; padding: 12px; background: #F3E8FF; border-radius: 12px; min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1.6s;">🦅</div>
                    <div style="font-size: 12px; margin-top: 5px; font-weight: bold;">Aerial</div>
                    <div style="font-size: 11px; color: #6B21A8;">The sky:<br>birds, bats</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "body_coverings_1":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #ECFDF5, #D1FAE5);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #065F46;">🎬 Body Coverings — Nature's Armour</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 35px; animation: bounce 1.8s ease-in-out infinite;">🪶</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Feathers</div>
                    <div style="font-size: 11px; color: #6B7280;">Birds — fly<br>& stay warm</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 35px; animation: bounce 1.8s ease-in-out infinite 0.3s;">🐍</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Scales</div>
                    <div style="font-size: 11px; color: #6B7280;">Fish & reptiles<br>— protection</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 35px; animation: bounce 1.8s ease-in-out infinite 0.6s;">🐢</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Shell</div>
                    <div style="font-size: 11px; color: #6B7280;">Tortoise, snail<br>— hard home</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 35px; animation: bounce 1.8s ease-in-out infinite 0.9s;">🐑</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Wool</div>
                    <div style="font-size: 11px; color: #6B7280;">Sheep — traps<br>air, warmth</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 35px; animation: bounce 1.8s ease-in-out infinite 1.2s;">🐻‍❄️</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Fur</div>
                    <div style="font-size: 11px; color: #6B7280;">Polar bear<br>— insulation</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "body_coverings_2":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FEF9C3, #FEF08A);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #854D0E;">🎬 Special Defence — Hide or Fight!</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite;">🦓</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Camouflage</div>
                    <div style="font-size: 11px; color: #6B7280;">Stripes & colours<br>to blend in</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.4s;">🪲</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Cuticle</div>
                    <div style="font-size: 11px; color: #6B7280;">Hard outer shell<br>on insects</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.8s;">🦔</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Quills</div>
                    <div style="font-size: 11px; color: #6B7280;">Sharp spines<br>scare enemies</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1.2s;">🛡️</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Armour Plates</div>
                    <div style="font-size: 11px; color: #6B7280;">Armadillo curls<br>into a ball</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 100px;">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1.6s;">🦎</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Colour Change</div>
                    <div style="font-size: 11px; color: #6B7280;">Chameleon<br>matches surroundings</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "herbivore_teeth":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #F0FDF4, #BBF7D0);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #166534;">🎬 Herbivore Feeding System</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 15px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 15px; background: white; border-radius: 50%; width: 90px; height: 90px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 30px;">🌿</div>
                    <div style="font-size: 10px;">Plants</div>
                </div>
                <div style="font-size: 24px; color: #22C55E; animation: bounce 1s infinite;">→</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 50%; width: 90px; height: 90px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 30px;">🦷</div>
                    <div style="font-size: 10px;">Sharp Front<br>Teeth (bite)</div>
                </div>
                <div style="font-size: 24px; color: #22C55E; animation: bounce 1s infinite 0.3s;">→</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 50%; width: 90px; height: 90px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 30px;">🔲</div>
                    <div style="font-size: 10px;">Flat Molars<br>(grind)</div>
                </div>
                <div style="font-size: 24px; color: #22C55E; animation: bounce 1s infinite 0.6s;">→</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 50%; width: 90px; height: 90px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 30px;">🐄</div>
                    <div style="font-size: 10px;">Long Gut<br>(digestion)</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px; font-size: 12px; color: #166534;">
                🦌 Deer &nbsp; 🐴 Horse &nbsp; 🐄 Cow &nbsp; 🐰 Rabbit &nbsp; — all herbivores with hard hooves
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "carnivore_feeders":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FEF2F2, #FECACA);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #991B1B;">🎬 Carnivores & Special Feeders</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 12px;">
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 110px;">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite;">🦁</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Carnivore</div>
                    <div style="font-size: 10px; color: #6B7280;">Sharp teeth 🔪<br>+ Claws for prey</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 110px;">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite 0.3s;">🐻</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Omnivore</div>
                    <div style="font-size: 10px; color: #6B7280;">Mixed teeth<br>Plants + Meat</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 110px;">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite 0.6s;">🐿️</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Rodent</div>
                    <div style="font-size: 10px; color: #6B7280;">Ever-growing<br>front teeth 🦷</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 110px;">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite 0.9s;">🦋</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Proboscis</div>
                    <div style="font-size: 10px; color: #6B7280;">Coiled tube<br>sucks nectar 🌸</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 110px;">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite 1.2s;">🦟</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Needle Tube</div>
                    <div style="font-size: 10px; color: #6B7280;">Pierces skin<br>sucks blood 💉</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "spiracles_skin":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #EDE9FE, #DDD6FE);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #5B21B6;">🎬 Unique Breathing — Insects & Earthworms</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
                <div style="text-align: center; padding: 20px; background: white; border-radius: 16px; box-shadow: 0 3px 12px rgba(0,0,0,0.1); flex: 1; min-width: 200px;">
                    <div style="font-size: 40px; animation: bounce 2s ease-in-out infinite;">🦗</div>
                    <div style="font-size: 14px; font-weight: bold; margin: 8px 0; color: #5B21B6;">Insect Breathing</div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;">
                        <span style="background: #EDE9FE; padding: 4px 8px; border-radius: 8px; font-size: 11px;">Spiracles (holes)</span>
                        <span style="color: #7C3AED;">→</span>
                        <span style="background: #EDE9FE; padding: 4px 8px; border-radius: 8px; font-size: 11px;">Trachea (tubes)</span>
                        <span style="color: #7C3AED;">→</span>
                        <span style="background: #EDE9FE; padding: 4px 8px; border-radius: 8px; font-size: 11px;">Body cells</span>
                    </div>
                    <div style="font-size: 11px; color: #6B7280; margin-top: 8px;">No lungs needed! Air goes directly to cells.</div>
                </div>
                <div style="text-align: center; padding: 20px; background: white; border-radius: 16px; box-shadow: 0 3px 12px rgba(0,0,0,0.1); flex: 1; min-width: 200px;">
                    <div style="font-size: 40px; animation: bounce 2s ease-in-out infinite 0.5s;">🪱</div>
                    <div style="font-size: 14px; font-weight: bold; margin: 8px 0; color: #5B21B6;">Earthworm Breathing</div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;">
                        <span style="background: #EDE9FE; padding: 4px 8px; border-radius: 8px; font-size: 11px;">Moist skin</span>
                        <span style="color: #7C3AED;">→</span>
                        <span style="background: #EDE9FE; padding: 4px 8px; border-radius: 8px; font-size: 11px;">O₂ dissolves</span>
                        <span style="color: #7C3AED;">→</span>
                        <span style="background: #EDE9FE; padding: 4px 8px; border-radius: 8px; font-size: 11px;">Into blood</span>
                    </div>
                    <div style="font-size: 11px; color: #6B7280; margin-top: 8px;">Must stay moist! Dries out = can't breathe.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "land_movement":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FFF7ED, #FED7AA);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #9A3412;">🎬 How Animals Move on Land</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 32px; animation: bounce 1.5s ease-in-out infinite;">🐕</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Walking</div>
                    <div style="font-size: 10px; color: #6B7280;">4 legs</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 32px; animation: bounce 1.5s ease-in-out infinite 0.3s;">🦎</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Crawling</div>
                    <div style="font-size: 10px; color: #6B7280;">Low body</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 32px; animation: bounce 1.5s ease-in-out infinite 0.6s;">🐍</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Slithering</div>
                    <div style="font-size: 10px; color: #6B7280;">No legs!</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 32px; animation: bounce 1.5s ease-in-out infinite 0.9s;">🐜</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">6 Legs</div>
                    <div style="font-size: 10px; color: #6B7280;">Insects</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 90px;">
                    <div style="font-size: 32px; animation: bounce 1.5s ease-in-out infinite 1.2s;">🦘</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Hopping</div>
                    <div style="font-size: 10px; color: #6B7280;">Strong legs</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px;">
                <div style="display: inline-block; background: #FEF3C7; padding: 8px 15px; border-radius: 20px; font-size: 12px;">
                    🐍 Snakes use: <strong>Belly scales</strong> + <strong>S-shaped muscles</strong> + <strong>Flexible backbone</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "migration_map":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #EFF6FF, #BFDBFE);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #1E40AF;">🎬 Epic Migration Routes</div>
            <div style="display: flex; flex-direction: column; gap: 10px; max-width: 500px; margin: 0 auto;">
                <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 10px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); animation: bounce 2s ease-in-out infinite;">
                    <span style="font-size: 28px;">🏔️</span>
                    <span style="font-size: 20px; color: #3B82F6;">✈️→</span>
                    <span style="font-size: 28px;">🇮🇳</span>
                    <span style="font-size: 12px; flex: 1;"><strong>Siberian Crane</strong><br>Russia → India (5000+ km)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 10px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); animation: bounce 2s ease-in-out infinite 0.3s;">
                    <span style="font-size: 28px;">🧊</span>
                    <span style="font-size: 20px; color: #3B82F6;">✈️→</span>
                    <span style="font-size: 28px;">🐧</span>
                    <span style="font-size: 12px; flex: 1;"><strong>Arctic Tern</strong><br>Arctic ↔ Antarctic (70,000 km!)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 10px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); animation: bounce 2s ease-in-out infinite 0.6s;">
                    <span style="font-size: 28px;">🦋</span>
                    <span style="font-size: 20px; color: #3B82F6;">✈️→</span>
                    <span style="font-size: 28px;">🌮</span>
                    <span style="font-size: 12px; flex: 1;"><strong>Monarch Butterfly</strong><br>Canada → Mexico (4000 km)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 10px 15px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); animation: bounce 2s ease-in-out infinite 0.9s;">
                    <span style="font-size: 28px;">🐢</span>
                    <span style="font-size: 20px; color: #3B82F6;">🏊→</span>
                    <span style="font-size: 28px;">🏖️</span>
                    <span style="font-size: 12px; flex: 1;"><strong>Olive Ridley Turtle</strong><br>Ocean → Odisha, India</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "skeleton_functions":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #F5F3FF, #EDE9FE);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #5B21B6;">🎬 What Does Your Skeleton Do?</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 95px;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite;">🏗️</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Shape</div>
                    <div style="font-size: 10px; color: #6B7280;">Gives body<br>its form</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 95px;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite 0.3s;">🧍</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Support</div>
                    <div style="font-size: 10px; color: #6B7280;">Stand<br>upright</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 95px;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite 0.6s;">🛡️</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Protect</div>
                    <div style="font-size: 10px; color: #6B7280;">Brain, heart<br>lungs, spine</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 95px;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite 0.9s;">🏃</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Movement</div>
                    <div style="font-size: 10px; color: #6B7280;">With muscles<br>at joints</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 95px;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite 1.2s;">🩸</div>
                    <div style="font-size: 11px; font-weight: bold; margin-top: 5px;">Blood Cells</div>
                    <div style="font-size: 10px; color: #6B7280;">Made in<br>bone marrow</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "bone_structure":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FFF7ED, #FFEDD5);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #9A3412;">🎬 Inside a Bone — Layers Revealed</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 15px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite;">🦴</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Compact Bone</div>
                    <div style="font-size: 10px; color: #6B7280;">(Hard outer layer)</div>
                </div>
                <div style="font-size: 24px; color: #EA580C;">→</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 0.5s;">🧽</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Spongy Bone</div>
                    <div style="font-size: 10px; color: #6B7280;">(Lightweight inside)</div>
                </div>
                <div style="font-size: 24px; color: #EA580C;">→</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 35px; animation: bounce 2s ease-in-out infinite 1s;">🩸</div>
                    <div style="font-size: 12px; font-weight: bold; margin-top: 5px;">Bone Marrow</div>
                    <div style="font-size: 10px; color: #6B7280;">(Makes blood cells)</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px; font-size: 12px; background: #FEF3C7; padding: 8px; border-radius: 8px;">
                + Nerves (feel pain) + Blood Vessels (nutrients) + Calcium (strength)
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "skull_parts":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #F0F9FF, #E0F2FE);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #0C4A6E;">🎬 The Skull — 22 Bones</div>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 20px; background: white; border-radius: 16px; box-shadow: 0 3px 12px rgba(0,0,0,0.1); min-width: 150px;">
                    <div style="font-size: 45px; animation: bounce 2s ease-in-out infinite;">🧠</div>
                    <div style="font-size: 14px; font-weight: bold; margin-top: 8px; color: #0C4A6E;">Cranium</div>
                    <div style="font-size: 22px; font-weight: bold; color: #0284C7;">8 bones</div>
                    <div style="font-size: 11px; color: #6B7280;">Protects the brain</div>
                </div>
                <div style="text-align: center; padding: 20px; background: white; border-radius: 16px; box-shadow: 0 3px 12px rgba(0,0,0,0.1); min-width: 150px;">
                    <div style="font-size: 45px; animation: bounce 2s ease-in-out infinite 0.5s;">😊</div>
                    <div style="font-size: 14px; font-weight: bold; margin-top: 8px; color: #0C4A6E;">Face</div>
                    <div style="font-size: 22px; font-weight: bold; color: #0284C7;">14 bones</div>
                    <div style="font-size: 11px; color: #6B7280;">Gives face its shape</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px; background: #DBEAFE; padding: 10px; border-radius: 10px;">
                <span style="font-size: 13px;">👄 Only the <strong>lower jaw</strong> can move! (eating, talking, yawning)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "skeleton_parts":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #ECFDF5, #D1FAE5);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #065F46;">🎬 The Complete Skeleton</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 8px;">
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); min-width: 85px;">
                    <div style="font-size: 28px; animation: bounce 1.8s ease-in-out infinite;">🔗</div>
                    <div style="font-size: 11px; font-weight: bold;">Backbone</div>
                    <div style="font-size: 10px; color: #065F46;">33 vertebrae</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); min-width: 85px;">
                    <div style="font-size: 28px; animation: bounce 1.8s ease-in-out infinite 0.3s;">🫁</div>
                    <div style="font-size: 11px; font-weight: bold;">Ribcage</div>
                    <div style="font-size: 10px; color: #065F46;">12 pairs + sternum</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); min-width: 85px;">
                    <div style="font-size: 28px; animation: bounce 1.8s ease-in-out infinite 0.6s;">💪</div>
                    <div style="font-size: 11px; font-weight: bold;">Arms</div>
                    <div style="font-size: 10px; color: #065F46;">Humerus, Radius, Ulna</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); min-width: 85px;">
                    <div style="font-size: 28px; animation: bounce 1.8s ease-in-out infinite 0.9s;">🦵</div>
                    <div style="font-size: 11px; font-weight: bold;">Legs</div>
                    <div style="font-size: 10px; color: #065F46;">Femur, Tibia, Fibula</div>
                </div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); min-width: 85px;">
                    <div style="font-size: 28px; animation: bounce 1.8s ease-in-out infinite 1.2s;">⭕</div>
                    <div style="font-size: 11px; font-weight: bold;">Girdles</div>
                    <div style="font-size: 10px; color: #065F46;">Shoulder + Hip</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 12px; font-size: 11px; background: #D1FAE5; padding: 8px; border-radius: 8px;">
                🪢 <strong>Ligaments</strong> hold bones together | <strong>Femur</strong> = longest bone | <strong>Floating ribs</strong> = last 2 pairs
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "ball_socket_joint":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FDF4FF, #FAE8FF);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #86198F;">🎬 Ball and Socket Joint</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 20px; background: white; border-radius: 50%; width: 110px; height: 110px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite;">⚽</div>
                    <div style="font-size: 10px;">Ball in cup</div>
                </div>
                <div style="font-size: 24px; color: #A855F7;">↔️↕️🔄</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <div style="font-size: 13px; font-weight: bold; color: #86198F;">ALL directions!</div>
                    <div style="margin-top: 8px; display: flex; gap: 12px;">
                        <div style="text-align: center;"><div style="font-size: 25px; animation: bounce 1.5s infinite;">💪</div><div style="font-size: 10px;">Shoulder</div></div>
                        <div style="text-align: center;"><div style="font-size: 25px; animation: bounce 1.5s infinite 0.3s;">🦵</div><div style="font-size: 10px;">Hip</div></div>
                        <div style="text-align: center;"><div style="font-size: 25px; animation: bounce 1.5s infinite 0.6s;">🕹️</div><div style="font-size: 10px;">Joystick!</div></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "hinge_joint":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FEF9C3, #FEF08A);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #854D0E;">🎬 Hinge Joint — One Direction Only!</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 15px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite;">🚪</div>
                    <div style="font-size: 11px; font-weight: bold;">Like a Door</div>
                    <div style="font-size: 10px; color: #6B7280;">ONE way only</div>
                </div>
                <div style="font-size: 24px; color: #CA8A04;">=</div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="font-size: 28px; animation: bounce 1.5s infinite 0.2s;">💪</div>
                    <div style="font-size: 10px;">Elbow</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="font-size: 28px; animation: bounce 1.5s infinite 0.4s;">🦵</div>
                    <div style="font-size: 10px;">Knee</div>
                </div>
                <div style="text-align: center; padding: 12px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="font-size: 28px; animation: bounce 1.5s infinite 0.6s;">🖐️</div>
                    <div style="font-size: 10px;">Fingers</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 10px; background: #FEF3C7; padding: 6px; border-radius: 8px; font-size: 11px;">↕️ Back & forth ONLY — no rotation or sideways!</div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "pivot_gliding_joint":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #F0FDFA, #CCFBF1);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #134E4A;">🎬 Pivot & Gliding Joints</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                <div style="text-align: center; padding: 18px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); flex: 1; min-width: 160px;">
                    <div style="font-size: 38px; animation: bounce 2s ease-in-out infinite;">🔄</div>
                    <div style="font-size: 13px; font-weight: bold; margin: 6px 0; color: #134E4A;">Pivot Joint</div>
                    <div style="font-size: 11px; color: #6B7280;">One bone rotates around another</div>
                    <div style="margin-top: 6px; background: #CCFBF1; padding: 5px; border-radius: 8px; font-size: 11px;">🙆 <strong>Neck</strong> — turn & nod</div>
                </div>
                <div style="text-align: center; padding: 18px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); flex: 1; min-width: 160px;">
                    <div style="font-size: 38px; animation: bounce 2s ease-in-out infinite 0.5s;">🫳</div>
                    <div style="font-size: 13px; font-weight: bold; margin: 6px 0; color: #134E4A;">Gliding Joint</div>
                    <div style="font-size: 11px; color: #6B7280;">Flat bones slide over each other</div>
                    <div style="margin-top: 6px; background: #CCFBF1; padding: 5px; border-radius: 8px; font-size: 11px;">✋ <strong>Wrist & Ankle</strong></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "muscle_contraction":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FEF2F2, #FECACA);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #991B1B;">🎬 How Muscles Move Bones</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 15px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite;">💪</div>
                    <div style="font-size: 12px; font-weight: bold;">Contract</div>
                    <div style="font-size: 10px; color: #6B7280;">Gets SHORT → Pulls bone</div>
                </div>
                <div style="font-size: 24px; color: #DC2626;">⟷</div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 35px; animation: bounce 1.5s ease-in-out infinite 0.5s;">🤲</div>
                    <div style="font-size: 12px; font-weight: bold;">Relax</div>
                    <div style="font-size: 10px; color: #6B7280;">Gets LONG → Bone returns</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 12px; display: inline-flex; align-items: center; gap: 5px; background: #FEE2E2; padding: 6px 12px; border-radius: 15px; font-size: 11px; margin-left: auto; margin-right: auto; width: fit-content;">
                🔗 Tendon joins 💪 Muscle to 🦴 Bone
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "muscle_types":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #FFF1F2, #FFE4E6);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #9F1239;">🎬 Three Types of Muscles</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; padding: 14px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); min-width: 130px; flex: 1;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite;">🦓</div>
                    <div style="font-size: 12px; font-weight: bold; color: #9F1239;">Striped (Voluntary)</div>
                    <div style="font-size: 10px; color: #6B7280;">YOU control them<br>Arms, legs<br>Can get tired</div>
                </div>
                <div style="text-align: center; padding: 14px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); min-width: 130px; flex: 1;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite 0.4s;">🫧</div>
                    <div style="font-size: 12px; font-weight: bold; color: #9F1239;">Smooth (Involuntary)</div>
                    <div style="font-size: 10px; color: #6B7280;">Automatic<br>Stomach, intestines<br>Brain controls</div>
                </div>
                <div style="text-align: center; padding: 14px; background: white; border-radius: 16px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); min-width: 130px; flex: 1;">
                    <div style="font-size: 32px; animation: bounce 2s ease-in-out infinite 0.8s;">❤️</div>
                    <div style="font-size: 12px; font-weight: bold; color: #9F1239;">Cardiac (Heart)</div>
                    <div style="font-size: 10px; color: #6B7280;">Only in heart<br>Works 24/7<br>Never tires!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "body_system_overview":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #EDE9FE, #DDD6FE);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #5B21B6;">🎬 How It All Works Together</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 6px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite;">🦴</div>
                    <div style="font-size: 10px; font-weight: bold;">Skeleton</div>
                </div>
                <div style="font-size: 16px; color: #7C3AED;">+</div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite 0.3s;">🔧</div>
                    <div style="font-size: 10px; font-weight: bold;">Joints</div>
                </div>
                <div style="font-size: 16px; color: #7C3AED;">+</div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite 0.6s;">💪</div>
                    <div style="font-size: 10px; font-weight: bold;">Muscles</div>
                </div>
                <div style="font-size: 16px; color: #7C3AED;">+</div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite 0.9s;">🧠</div>
                    <div style="font-size: 10px; font-weight: bold;">Brain Signal</div>
                </div>
                <div style="font-size: 16px; color: #7C3AED;">=</div>
                <div style="text-align: center; padding: 10px; background: #7C3AED; border-radius: 12px; color: white;">
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite 1.2s;">🏃</div>
                    <div style="font-size: 10px; font-weight: bold;">Movement!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


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

    # ─── Scene Title ──────────────────────────────────────────────────────────
    st.header(scene["title"])

    # ─── Character + Narration ────────────────────────────────────────────────
    col_content, col_char = st.columns([3, 1])

    with col_content:
        # Speaker tag
        character_name = scene.get("character", "Tara").title()
        st.markdown(f"**🎭 {character_name}**")

        st.write("")
        st.write(scene["narration"])

        # TTS audio
        if scene.get("tts"):
            with st.expander("🔊 Listen to Narration"):
                render_audio_player(scene["narration"], scene["id"])

    with col_char:
        character_file = Path(f"assets/characters/{scene['character']}.png")
        if character_file.exists():
            st.image(str(character_file), width=200)

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
    if "summary" in scene:
        summary = scene["summary"]
        st.write("")
        st.subheader("📋 Chapter Summary")
        for point in summary.get("points", []):
            st.write(f"• {point}")
        if "key_terms" in summary:
            st.write("")
            st.write("**Key Terms:**")
            for term in summary["key_terms"]:
                st.write(f"  **{term['term']}** — {term['definition']}")

    # ─── Badge Award ──────────────────────────────────────────────────────────
    if scene.get("scene_type") == "badge":
        st.write("")
        badge_name = scene.get("badge", chapter_data.get("badge", "Achievement"))
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #FEF3C7, #FDE68A); border-radius: 20px; margin: 20px 0;">
            <div style="font-size: 64px;">🏆</div>
            <h2 style="color: #92400E;">Congratulations, {st.session_state.student_name}!</h2>
            <h3 style="color: #B45309;">You earned the "{badge_name}" badge!</h3>
            <p style="color: #78350F;">You have completed Chapter {ch_id} successfully!</p>
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
            st.session_state.chapter_started = False
            st.session_state.scene_index = 0
            st.rerun()

    with col_next:
        if st.session_state.scene_index < scene_count - 1:
            if st.button("Next ➡", key="nav_next"):
                st.session_state.scene_index += 1
                st.rerun()
        else:
            if st.button("🏁 Finish Chapter", key="nav_finish"):
                st.session_state.chapter_started = False
                st.session_state.scene_index = 0
                st.rerun()

# ─── Footer ──────────────────────────────────────────────────────────────────

st.divider()
st.caption("WonderLearn © 2026 | Learn Through Stories, Explore Through Adventures")
