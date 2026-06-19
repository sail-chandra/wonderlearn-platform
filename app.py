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
    """Render interactive HTML5 Canvas/JS animations for motion-based concept demos."""

    if anim_type == "habitat_types":
        components.html("""
        <div style="background: linear-gradient(135deg, #FEF3C7, #ECFDF5); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#92400E; margin:0 0 15px;">🎬 Animal Habitats — Where Do They Live?</h4>
        <canvas id="c" width="580" height="260"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0;
        const habitats=[
            {x:60,y:130,icon:'🦁',label:'Terrestrial',color:'#D1FAE5',desc:'Land'},
            {x:175,y:130,icon:'🐟',label:'Aquatic',color:'#DBEAFE',desc:'Water'},
            {x:290,y:130,icon:'🐸',label:'Amphibious',color:'#E0E7FF',desc:'Both'},
            {x:405,y:130,icon:'🐒',label:'Arboreal',color:'#D1FAE5',desc:'Trees'},
            {x:520,y:130,icon:'🦅',label:'Aerial',color:'#F3E8FF',desc:'Sky'}
        ];
        function draw(){
            ctx.clearRect(0,0,580,260);
            habitats.forEach((h,i)=>{
                let bounce=Math.sin(t*0.03+i*1.2)*8;
                // Background circle
                ctx.beginPath();ctx.arc(h.x,h.y+bounce,45,0,Math.PI*2);
                ctx.fillStyle=h.color;ctx.fill();
                ctx.strokeStyle='#9CA3AF';ctx.lineWidth=2;ctx.stroke();
                // Icon
                ctx.font='32px serif';ctx.textAlign='center';
                ctx.fillText(h.icon,h.x,h.y+bounce+10);
                // Label
                ctx.font='bold 12px sans-serif';ctx.fillStyle='#1F2937';
                ctx.fillText(h.label,h.x,h.y+bounce+55);
                ctx.font='11px sans-serif';ctx.fillStyle='#6B7280';
                ctx.fillText(h.desc,h.x,h.y+bounce+70);
            });
            // Animated arrow cycling between habitats
            let arrowIdx=Math.floor(t*0.02)%5;
            ctx.beginPath();ctx.arc(habitats[arrowIdx].x,habitats[arrowIdx].y-55,8,0,Math.PI*2);
            ctx.fillStyle='#F59E0B';ctx.fill();
            ctx.font='12px sans-serif';ctx.fillStyle='#92400E';
            ctx.fillText('▼',habitats[arrowIdx].x,habitats[arrowIdx].y-48);
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=320)
        return True

    elif anim_type == "body_coverings_1":
        components.html("""
        <div style="background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#065F46; margin:0 0 10px;">🎬 Body Coverings — Nature's Armour</h4>
        <canvas id="c" width="580" height="280"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0,selected=-1;
        const items=[
            {x:60,y:100,icon:'🪶',name:'Feathers',animal:'Birds',purpose:'Fly & warmth',color:'#FEF3C7'},
            {x:175,y:100,icon:'🐍',name:'Scales',animal:'Fish/Reptiles',purpose:'Protection',color:'#DBEAFE'},
            {x:290,y:100,icon:'🐢',name:'Shell',animal:'Tortoise/Snail',purpose:'Hard home',color:'#F3E8FF'},
            {x:405,y:100,icon:'🐑',name:'Wool',animal:'Sheep',purpose:'Trap warmth',color:'#FEF9C3'},
            {x:520,y:100,icon:'🐻‍❄️',name:'Fur',animal:'Polar Bear',purpose:'Insulation',color:'#E0F2FE'}
        ];
        c.addEventListener('click',e=>{
            const r=c.getBoundingClientRect();
            const mx=e.clientX-r.left,my=e.clientY-r.top;
            selected=-1;
            items.forEach((it,i)=>{if(Math.abs(mx-it.x)<40&&Math.abs(my-it.y)<40)selected=i;});
        });
        function draw(){
            ctx.clearRect(0,0,580,280);
            items.forEach((it,i)=>{
                let s=selected===i?1.15:1;
                let bounce=Math.sin(t*0.04+i*1.3)*5;
                // Card
                ctx.save();ctx.translate(it.x,it.y+bounce);ctx.scale(s,s);
                ctx.beginPath();ctx.roundRect(-40,-40,80,80,12);
                ctx.fillStyle=it.color;ctx.fill();
                ctx.strokeStyle=selected===i?'#22C55E':'#D1D5DB';ctx.lineWidth=selected===i?3:1;ctx.stroke();
                ctx.font='30px serif';ctx.textAlign='center';ctx.fillText(it.icon,0,10);
                ctx.restore();
                // Labels below
                ctx.font='bold 11px sans-serif';ctx.fillStyle='#1F2937';ctx.textAlign='center';
                ctx.fillText(it.name,it.x,it.y+bounce+55);
                ctx.font='10px sans-serif';ctx.fillStyle='#6B7280';
                ctx.fillText(it.animal,it.x,it.y+bounce+68);
            });
            // Detail panel
            if(selected>=0){
                let it=items[selected];
                ctx.fillStyle='#F0FDF4';ctx.beginPath();ctx.roundRect(90,200,400,50,10);ctx.fill();
                ctx.strokeStyle='#22C55E';ctx.lineWidth=2;ctx.stroke();
                ctx.font='14px sans-serif';ctx.fillStyle='#065F46';ctx.textAlign='center';
                ctx.fillText(it.icon+' '+it.name+' — '+it.purpose+' (Found on: '+it.animal+')',290,230);
            } else {
                ctx.font='12px sans-serif';ctx.fillStyle='#9CA3AF';ctx.textAlign='center';
                ctx.fillText('👆 Click on any covering to learn more!',290,230);
            }
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=340)
        return True

    elif anim_type == "body_coverings_2":
        components.html("""
        <div style="background: linear-gradient(135deg, #FEF9C3, #FEF08A); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#854D0E; margin:0 0 10px;">🎬 Special Defence — Hide or Fight!</h4>
        <canvas id="c" width="580" height="280"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0,selected=-1;
        const items=[
            {x:60,y:100,icon:'🦓',name:'Camouflage',desc:'Stripes/colour blend with surroundings',color:'#F3F4F6'},
            {x:175,y:100,icon:'🪲',name:'Cuticle',desc:'Hard outer layer on insects like armour',color:'#FEF3C7'},
            {x:290,y:100,icon:'🦔',name:'Quills',desc:'Sharp spines raised to scare enemies',color:'#FEE2E2'},
            {x:405,y:100,icon:'🛡️',name:'Armour Plates',desc:'Bony plates — armadillo curls into ball',color:'#E0E7FF'},
            {x:520,y:100,icon:'🦎',name:'Colour Change',desc:'Chameleon matches any background',color:'#D1FAE5'}
        ];
        c.addEventListener('click',e=>{
            const r=c.getBoundingClientRect();
            const mx=e.clientX-r.left,my=e.clientY-r.top;
            selected=-1;
            items.forEach((it,i)=>{if(Math.abs(mx-it.x)<40&&Math.abs(my-it.y)<40)selected=i;});
        });
        function draw(){
            ctx.clearRect(0,0,580,280);
            // Camouflage demo - zebra fading in/out
            if(selected===0){
                let alpha=0.3+0.7*Math.abs(Math.sin(t*0.05));
                ctx.globalAlpha=alpha;
            }
            items.forEach((it,i)=>{
                ctx.globalAlpha=1;
                let pulse=selected===i?3+Math.sin(t*0.1)*3:0;
                let bounce=Math.sin(t*0.04+i)*5;
                ctx.beginPath();ctx.roundRect(it.x-40,it.y+bounce-40,80,80,12);
                ctx.fillStyle=it.color;ctx.fill();
                ctx.strokeStyle=selected===i?'#EAB308':'#D1D5DB';
                ctx.lineWidth=selected===i?3:1;ctx.stroke();
                ctx.font='30px serif';ctx.textAlign='center';
                ctx.fillText(it.icon,it.x,it.y+bounce+10);
                ctx.font='bold 10px sans-serif';ctx.fillStyle='#1F2937';
                ctx.fillText(it.name,it.x,it.y+bounce+55);
            });
            if(selected>=0){
                ctx.fillStyle='#FFFBEB';ctx.beginPath();ctx.roundRect(90,195,400,55,10);ctx.fill();
                ctx.strokeStyle='#EAB308';ctx.lineWidth=2;ctx.stroke();
                ctx.font='13px sans-serif';ctx.fillStyle='#78350F';ctx.textAlign='center';
                ctx.fillText(items[selected].icon+' '+items[selected].name,290,217);
                ctx.font='12px sans-serif';ctx.fillStyle='#92400E';
                ctx.fillText(items[selected].desc,290,237);
            } else {
                ctx.font='12px sans-serif';ctx.fillStyle='#9CA3AF';ctx.textAlign='center';
                ctx.fillText('👆 Click on a defence mechanism to see it in action!',290,225);
            }
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=340)
        return True

    elif anim_type == "herbivore_teeth":
        components.html("""
        <div style="background: linear-gradient(135deg, #F0FDF4, #BBF7D0); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#166534; margin:0 0 10px;">🎬 Herbivore Feeding System</h4>
        <canvas id="c" width="580" height="240"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0;
        function draw(){
            ctx.clearRect(0,0,580,240);
            // Animated flow: Plant → Bite → Grind → Digest
            const steps=[
                {x:80,icon:'🌿',label:'Plant Food',sub:'leaves, grass'},
                {x:210,icon:'🦷',label:'Sharp Incisors',sub:'bite & cut'},
                {x:340,icon:'🔲',label:'Flat Molars',sub:'grind & crush'},
                {x:470,icon:'🐄',label:'Long Gut',sub:'slow digestion'}
            ];
            // Animated food particle traveling
            let foodX=80+(t*1.5)%480;
            ctx.beginPath();ctx.arc(foodX,40,6,0,Math.PI*2);
            ctx.fillStyle='#22C55E';ctx.fill();
            ctx.font='10px sans-serif';ctx.fillStyle='#166534';ctx.textAlign='center';
            ctx.fillText('🌱',foodX,44);

            steps.forEach((s,i)=>{
                let bounce=Math.sin(t*0.04+i)*6;
                // Circle
                ctx.beginPath();ctx.arc(s.x,110+bounce,40,0,Math.PI*2);
                ctx.fillStyle='white';ctx.fill();
                ctx.strokeStyle='#22C55E';ctx.lineWidth=2;ctx.stroke();
                ctx.font='28px serif';ctx.textAlign='center';
                ctx.fillText(s.icon,s.x,120+bounce);
                // Arrow
                if(i<3){
                    ctx.beginPath();ctx.moveTo(s.x+45,110);ctx.lineTo(s.x+85,110);
                    ctx.strokeStyle='#16A34A';ctx.lineWidth=2;ctx.stroke();
                    ctx.beginPath();ctx.moveTo(s.x+80,105);ctx.lineTo(s.x+88,110);ctx.lineTo(s.x+80,115);
                    ctx.fillStyle='#16A34A';ctx.fill();
                }
                ctx.font='bold 12px sans-serif';ctx.fillStyle='#1F2937';
                ctx.fillText(s.label,s.x,170+bounce);
                ctx.font='10px sans-serif';ctx.fillStyle='#6B7280';
                ctx.fillText(s.sub,s.x,185+bounce);
            });
            // Bottom bar
            ctx.font='11px sans-serif';ctx.fillStyle='#166534';ctx.textAlign='center';
            ctx.fillText('🦌 Deer  🐴 Horse  🐄 Cow  🐰 Rabbit — all have hard hooves for walking long distances',290,220);
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=300)
        return True

    elif anim_type == "carnivore_feeders":
        components.html("""
        <div style="background: linear-gradient(135deg, #FEF2F2, #FECACA); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#991B1B; margin:0 0 10px;">🎬 Carnivores & Special Feeders</h4>
        <canvas id="c" width="580" height="280"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0,selected=-1;
        const items=[
            {x:60,y:100,icon:'🦁',name:'Carnivore',tool:'Sharp teeth + Claws',food:'Meat only',color:'#FEE2E2'},
            {x:175,y:100,icon:'🐻',name:'Omnivore',tool:'Mixed teeth',food:'Plants + Meat',color:'#FEF3C7'},
            {x:290,y:100,icon:'🐿️',name:'Rodent',tool:'Ever-growing teeth',food:'Nuts & seeds',color:'#E0F2FE'},
            {x:405,y:100,icon:'🦋',name:'Proboscis',tool:'Coiled tube',food:'Nectar',color:'#F3E8FF'},
            {x:520,y:100,icon:'🦟',name:'Needle tube',tool:'Piercing tube',food:'Blood',color:'#FCE7F3'}
        ];
        c.addEventListener('click',e=>{
            const r=c.getBoundingClientRect();
            const mx=e.clientX-r.left,my=e.clientY-r.top;
            selected=-1;
            items.forEach((it,i)=>{if(Math.abs(mx-it.x)<40&&Math.abs(my-it.y)<40)selected=i;});
        });
        function draw(){
            ctx.clearRect(0,0,580,280);
            items.forEach((it,i)=>{
                let bounce=Math.sin(t*0.04+i*1.2)*5;
                let s=selected===i?1.1:1;
                ctx.save();ctx.translate(it.x,it.y+bounce);ctx.scale(s,s);
                ctx.beginPath();ctx.roundRect(-38,-38,76,76,12);
                ctx.fillStyle=it.color;ctx.fill();
                ctx.strokeStyle=selected===i?'#DC2626':'#E5E7EB';ctx.lineWidth=selected===i?3:1;ctx.stroke();
                ctx.font='28px serif';ctx.textAlign='center';ctx.fillText(it.icon,0,8);
                ctx.restore();
                ctx.font='bold 10px sans-serif';ctx.fillStyle='#1F2937';ctx.textAlign='center';
                ctx.fillText(it.name,it.x,it.y+bounce+52);
            });
            // Animated feeding demo for selected
            if(selected>=0){
                let it=items[selected];
                ctx.fillStyle='#FFF';ctx.beginPath();ctx.roundRect(80,190,420,60,10);ctx.fill();
                ctx.strokeStyle='#DC2626';ctx.lineWidth=1.5;ctx.stroke();
                ctx.font='13px sans-serif';ctx.fillStyle='#991B1B';ctx.textAlign='center';
                ctx.fillText(it.icon+' '+it.name+': '+it.tool,290,212);
                ctx.font='12px sans-serif';ctx.fillStyle='#6B7280';
                ctx.fillText('Food: '+it.food,290,232);
                // Mini feeding animation
                let fx=180+Math.sin(t*0.08)*20;
                ctx.font='16px serif';ctx.fillText(it.icon,fx,245);
            } else {
                ctx.font='12px sans-serif';ctx.fillStyle='#9CA3AF';ctx.textAlign='center';
                ctx.fillText('👆 Click an animal to see how it feeds!',290,220);
            }
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=340)
        return True

    elif anim_type == "breathing_systems":
        components.html("""
        <div style="background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#1E40AF; margin:0 0 10px;">🎬 How Animals Breathe — Watch the Flow!</h4>
        <canvas id="c" width="580" height="300"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0,selected=0;
        const systems=[
            {icon:'🫁',name:'Lungs',animal:'Mammals/Birds',flow:['Nostrils','Windpipe','Lungs','Blood (O₂)'],color:'#DBEAFE'},
            {icon:'🐟',name:'Gills',animal:'Fish/Tadpoles',flow:['Water in mouth','Over gills','O₂ absorbed','Blood carries'],color:'#D1FAE5'},
            {icon:'🦗',name:'Spiracles',animal:'Insects',flow:['Spiracle holes','Trachea tubes','Directly to cells','No blood needed'],color:'#EDE9FE'},
            {icon:'🪱',name:'Skin',animal:'Earthworm',flow:['Moist skin','O₂ dissolves','Into blood','Must stay wet!'],color:'#FEF3C7'},
            {icon:'🐋',name:'Blowhole',animal:'Whales/Dolphins',flow:['Surface','Blowhole opens','Air to lungs','Dive again'],color:'#E0F2FE'}
        ];
        // Tab buttons
        const tabs=document.createElement('div');
        tabs.style.cssText='display:flex;justify-content:center;gap:8px;margin-bottom:10px;';
        systems.forEach((s,i)=>{
            const btn=document.createElement('button');
            btn.textContent=s.icon+' '+s.name;
            btn.style.cssText='padding:5px 12px;border-radius:20px;border:2px solid '+(i===0?'#3B82F6':'#D1D5DB')+';background:'+(i===0?'#EFF6FF':'white')+';cursor:pointer;font-size:12px;';
            btn.onclick=()=>{selected=i;document.querySelectorAll('button').forEach((b,j)=>{b.style.border='2px solid '+(j===i?'#3B82F6':'#D1D5DB');b.style.background=j===i?'#EFF6FF':'white';});};
            tabs.appendChild(btn);
        });
        c.parentElement.insertBefore(tabs,c);
        function draw(){
            ctx.clearRect(0,0,580,300);
            let sys=systems[selected];
            // Title
            ctx.font='16px sans-serif';ctx.fillStyle='#1E40AF';ctx.textAlign='center';
            ctx.fillText(sys.icon+' '+sys.name+' — '+sys.animal,290,30);
            // Animated flow pipeline
            sys.flow.forEach((step,i)=>{
                let x=80+i*140,y=120;
                let progress=(t*0.02)%4;
                let active=Math.floor(progress)===i;
                // Box
                ctx.beginPath();ctx.roundRect(x-50,y-30,100,60,10);
                ctx.fillStyle=active?sys.color:'white';ctx.fill();
                ctx.strokeStyle=active?'#3B82F6':'#D1D5DB';ctx.lineWidth=active?3:1;ctx.stroke();
                ctx.font=(active?'bold ':'')+' 12px sans-serif';ctx.fillStyle='#1F2937';ctx.textAlign='center';
                ctx.fillText(step,x,y+5);
                // Arrow
                if(i<3){
                    let arrowX=x+55;
                    ctx.beginPath();ctx.moveTo(arrowX,y);ctx.lineTo(arrowX+25,y);
                    ctx.strokeStyle='#3B82F6';ctx.lineWidth=2;ctx.stroke();
                    ctx.beginPath();ctx.moveTo(arrowX+20,y-5);ctx.lineTo(arrowX+28,y);ctx.lineTo(arrowX+20,y+5);ctx.fillStyle='#3B82F6';ctx.fill();
                }
            });
            // Animated O2 particles
            for(let i=0;i<6;i++){
                let px=(t*2+i*100)%580,py=200+Math.sin(t*0.03+i)*20;
                ctx.beginPath();ctx.arc(px,py,4,0,Math.PI*2);
                ctx.fillStyle='rgba(59,130,246,0.5)';ctx.fill();
                ctx.font='8px sans-serif';ctx.fillStyle='#3B82F6';ctx.fillText('O₂',px,py+3);
            }
            // Info text
            ctx.font='11px sans-serif';ctx.fillStyle='#6B7280';ctx.textAlign='center';
            ctx.fillText('Oxygen flows through the system to reach body cells',290,270);
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=380)
        return True

    elif anim_type == "spiracles_skin":
        components.html("""
        <div style="background: linear-gradient(135deg, #EDE9FE, #DDD6FE); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#5B21B6; margin:0 0 10px;">🎬 Insect Spiracles vs Earthworm Skin Breathing</h4>
        <canvas id="c" width="580" height="260"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0;
        function draw(){
            ctx.clearRect(0,0,580,260);
            // LEFT: Insect spiracles
            ctx.font='bold 13px sans-serif';ctx.fillStyle='#5B21B6';ctx.textAlign='center';
            ctx.fillText('🦗 Insect — Spiracles',150,25);
            // Draw insect body
            ctx.beginPath();ctx.ellipse(150,100,60,30,0,0,Math.PI*2);
            ctx.fillStyle='#A78BFA';ctx.fill();ctx.strokeStyle='#7C3AED';ctx.lineWidth=2;ctx.stroke();
            // Spiracle holes with air going in
            for(let i=0;i<4;i++){
                let sx=100+i*30,sy=100;
                ctx.beginPath();ctx.arc(sx,sy+30,4,0,Math.PI*2);ctx.fillStyle='#FDE68A';ctx.fill();
                // Air arrow going in
                let airY=sy+30-10-Math.abs(Math.sin(t*0.05+i))*15;
                ctx.font='10px serif';ctx.fillText('💨',sx,airY);
            }
            // Trachea tubes inside
            ctx.setLineDash([3,3]);
            ctx.beginPath();ctx.moveTo(110,100);ctx.lineTo(190,100);ctx.strokeStyle='#EAB308';ctx.stroke();
            ctx.setLineDash([]);
            ctx.font='10px sans-serif';ctx.fillStyle='#6B7280';
            ctx.fillText('Spiracle holes → Trachea tubes → Cells',150,160);
            ctx.fillText('No lungs! Air goes directly to cells.',150,178);

            // RIGHT: Earthworm skin
            ctx.font='bold 13px sans-serif';ctx.fillStyle='#5B21B6';ctx.textAlign='center';
            ctx.fillText('🪱 Earthworm — Skin',430,25);
            // Draw worm body
            let wormY=100+Math.sin(t*0.03)*5;
            ctx.beginPath();ctx.ellipse(430,wormY,50,18,0,0,Math.PI*2);
            ctx.fillStyle='#FBBF24';ctx.fill();ctx.strokeStyle='#D97706';ctx.lineWidth=2;ctx.stroke();
            // Moisture drops on skin
            for(let i=0;i<5;i++){
                let dx=395+i*18,dy=wormY-20+Math.sin(t*0.04+i)*3;
                ctx.font='8px serif';ctx.fillText('💧',dx,dy);
            }
            // O2 arrows going through skin
            for(let i=0;i<3;i++){
                let ox=410+i*20,oy=wormY+25+Math.sin(t*0.05+i)*5;
                ctx.font='9px sans-serif';ctx.fillStyle='#3B82F6';
                ctx.fillText('O₂↓',ox,oy);
            }
            ctx.font='10px sans-serif';ctx.fillStyle='#6B7280';
            ctx.fillText('Moist skin → O₂ dissolves → Into blood',430,160);
            ctx.fillText('Must stay wet or it cannot breathe!',430,178);

            // Divider
            ctx.beginPath();ctx.moveTo(290,20);ctx.lineTo(290,200);
            ctx.strokeStyle='#D1D5DB';ctx.lineWidth=1;ctx.setLineDash([5,5]);ctx.stroke();ctx.setLineDash([]);

            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=310)
        return True

    elif anim_type == "land_movement":
        components.html("""
        <div style="background: linear-gradient(135deg, #FFF7ED, #FED7AA); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#9A3412; margin:0 0 10px;">🎬 How Animals Move on Land</h4>
        <canvas id="c" width="580" height="250"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0;
        function draw(){
            ctx.clearRect(0,0,580,250);
            // Ground line
            ctx.beginPath();ctx.moveTo(0,200);ctx.lineTo(580,200);ctx.strokeStyle='#92400E';ctx.lineWidth=2;ctx.stroke();
            // Animals moving across screen
            const animals=[
                {icon:'🐕',y:175,speed:1.5,label:'Walk (4 legs)'},
                {icon:'🦎',y:185,speed:0.8,label:'Crawl'},
                {icon:'🐍',y:192,speed:1.2,label:'Slither (no legs!)'},
                {icon:'🐜',y:188,speed:2,label:'6 legs (insect)'},
                {icon:'🦘',y:160,speed:1.8,label:'Hop'}
            ];
            animals.forEach((a,i)=>{
                let x=(t*a.speed+i*120)%640-30;
                let hopBounce=a.icon==='🦘'?Math.abs(Math.sin(t*0.08))*25:0;
                let slither=a.icon==='🐍'?Math.sin(t*0.1)*8:0;
                ctx.font='28px serif';ctx.textAlign='center';
                ctx.fillText(a.icon,x,a.y-hopBounce+slither);
                // Label under each
                if(x>50&&x<530){
                    ctx.font='10px sans-serif';ctx.fillStyle='#78350F';
                    ctx.fillText(a.label,x,210);
                }
            });
            // Snake explanation
            ctx.font='11px sans-serif';ctx.fillStyle='#9A3412';ctx.textAlign='center';
            ctx.fillText('🐍 Snakes use: Belly scales + S-shaped muscles + Flexible backbone',290,238);
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=310)
        return True

    elif anim_type == "animal_movement":
        components.html("""
        <div style="background: linear-gradient(135deg, #F0FDF4, #DCFCE7); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#166534; margin:0 0 10px;">🎬 Flying & Swimming — Adaptations in Motion</h4>
        <canvas id="c" width="580" height="280"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0;
        function draw(){
            ctx.clearRect(0,0,580,280);
            // SKY section (top half)
            ctx.fillStyle='#EFF6FF';ctx.fillRect(0,0,580,130);
            ctx.font='bold 11px sans-serif';ctx.fillStyle='#1E40AF';ctx.textAlign='left';
            ctx.fillText('✈️ SKY',10,20);
            // Flying bird with wing flap
            let birdX=(t*1.5)%640-30;
            let wingY=Math.sin(t*0.12)*10;
            ctx.font='30px serif';ctx.textAlign='center';
            ctx.fillText('🦅',birdX,60+wingY);
            // Bird adaptations labels
            ctx.font='10px sans-serif';ctx.fillStyle='#1E40AF';ctx.textAlign='center';
            ctx.fillText('Hollow bones + Wings + Streamlined body + Tail steering',290,110);
            // Bat
            let batX=(t*1.2+200)%640-30;
            ctx.font='22px serif';ctx.fillText('🦇',batX,90+Math.sin(t*0.1+1)*8);

            // WATER section (bottom half)
            ctx.fillStyle='#DBEAFE';ctx.fillRect(0,135,580,145);
            ctx.font='bold 11px sans-serif';ctx.fillStyle='#0C4A6E';ctx.textAlign='left';
            ctx.fillText('🌊 WATER',10,152);
            // Swimming fish
            let fishX=(t*1.8)%640-30;
            ctx.font='28px serif';ctx.textAlign='center';
            ctx.fillText('🐠',fishX,190+Math.sin(t*0.06)*5);
            // Duck with webbed feet
            let duckX=(t*1.0+300)%640-30;
            ctx.font='24px serif';ctx.fillText('🦆',duckX,175);
            // Penguin swimming
            let penX=(t*1.4+150)%640-30;
            ctx.font='22px serif';ctx.fillText('🐧',penX,210+Math.sin(t*0.08+2)*5);
            // Water adaptations
            ctx.font='10px sans-serif';ctx.fillStyle='#0C4A6E';ctx.textAlign='center';
            ctx.fillText('Fins + Streamlined body + Webbed feet (ducks) + Flippers (penguins)',290,255);
            // Divider line
            ctx.beginPath();ctx.moveTo(0,133);ctx.lineTo(580,133);ctx.strokeStyle='#93C5FD';ctx.lineWidth=2;ctx.stroke();
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=340)
        return True

    elif anim_type == "migration_map":
        components.html("""
        <div style="background: linear-gradient(135deg, #EFF6FF, #BFDBFE); border-radius: 16px; padding: 20px; font-family: sans-serif;">
        <h4 style="text-align:center; color:#1E40AF; margin:0 0 10px;">🎬 Epic Migration Routes — Animals on the Move!</h4>
        <canvas id="c" width="580" height="300"></canvas>
        <script>
        const c=document.getElementById('c'),ctx=c.getContext('2d');
        let t=0;
        const routes=[
            {icon:'🏔️',from:'Siberia',to:'India',animal:'🦢 Siberian Crane',dist:'5000+ km',y:40,color:'#DBEAFE'},
            {icon:'🧊',from:'Arctic',to:'Antarctic',animal:'🕊️ Arctic Tern',dist:'70,000 km!',y:95,color:'#D1FAE5'},
            {icon:'🍁',from:'Canada',to:'Mexico',animal:'🦋 Monarch Butterfly',dist:'4000 km',y:150,color:'#FEF3C7'},
            {icon:'🌊',from:'Ocean',to:'Odisha, India',animal:'🐢 Olive Ridley Turtle',dist:'1000s km',y:205,color:'#FCE7F3'},
            {icon:'🏞️',from:'River birth',to:'Ocean & back',animal:'🐟 Salmon',dist:'Round trip!',y:260,color:'#E0E7FF'}
        ];
        function draw(){
            ctx.clearRect(0,0,580,300);
            routes.forEach((r,i)=>{
                // Background bar
                ctx.fillStyle=r.color;ctx.beginPath();ctx.roundRect(10,r.y,560,45,8);ctx.fill();
                // From label
                ctx.font='11px sans-serif';ctx.fillStyle='#6B7280';ctx.textAlign='left';
                ctx.fillText(r.from,20,r.y+18);
                // To label
                ctx.textAlign='right';ctx.fillText(r.to,570,r.y+18);
                // Animal moving along the route
                let progress=(t*0.005+i*0.2)%1;
                let animalX=60+progress*460;
                ctx.font='18px serif';ctx.textAlign='center';
                ctx.fillText(r.animal.split(' ')[0],animalX,r.y+38);
                // Dotted path
                ctx.setLineDash([4,4]);ctx.beginPath();
                ctx.moveTo(60,r.y+32);ctx.lineTo(540,r.y+32);
                ctx.strokeStyle='#9CA3AF';ctx.lineWidth=1;ctx.stroke();ctx.setLineDash([]);
                // Animal name + distance
                ctx.font='bold 11px sans-serif';ctx.fillStyle='#1F2937';ctx.textAlign='center';
                ctx.fillText(r.animal+' — '+r.dist,290,r.y+15);
            });
            t++;requestAnimationFrame(draw);
        }
        draw();
        </script></div>
        """, height=360)
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
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite 0.9s;">🔗</div>
                    <div style="font-size: 10px; font-weight: bold;">Tendons</div>
                </div>
                <div style="font-size: 16px; color: #7C3AED;">+</div>
                <div style="text-align: center; padding: 10px; background: white; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 28px; animation: bounce 1.5s ease-in-out infinite 1.2s;">🪢</div>
                    <div style="font-size: 10px; font-weight: bold;">Ligaments</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 12px; font-size: 13px; color: #5B21B6; font-weight: bold;">= YOU CAN MOVE! 🏃</div>
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

if "badges" not in st.session_state:
    st.session_state.badges = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "challenge_submitted" not in st.session_state:
    st.session_state.challenge_submitted = False

if "challenge_score" not in st.session_state:
    st.session_state.challenge_score = 0

if "activity_submitted" not in st.session_state:
    st.session_state.activity_submitted = False

if "activity_score" not in st.session_state:
    st.session_state.activity_score = 0

if "experiment_result" not in st.session_state:
    st.session_state.experiment_result = None


# ─── Header / Home Page ───────────────────────────────────────────────────────

st.title("🌟 WonderLearn")
st.subheader("Learn Through Stories, Explore Through Adventures")

col1, col2, col3 = st.columns(3)

with col1:
    student_name = st.text_input("Student Name", value="Explorer")

with col2:
    selected_class = st.selectbox("Class", ["Class 5"])

with col3:
    subject = st.selectbox("Subject", ["General Science"])

if not st.session_state.chapter_started:
    st.success(f"Welcome {student_name}! 🚀")

json_file = Path("content/class5/science/chapters.json")

if json_file.exists():
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

if not st.session_state.chapter_started:

    st.subheader("📚 Available Adventures")

    for chapter in data["chapters"]:

        st.markdown(
            f"### Chapter {chapter['id']} - {chapter['title']}"
        )

        st.write(
            f"🏆 Badge: {chapter['badge']}"
        )

        chapter_folder = Path(
            f"content/class5/science/chapter{chapter['id']}"
        )

        chapter_file = chapter_folder / "chapter.json"
        scene_file = chapter_folder / "scenes.json"

        if chapter_file.exists() and scene_file.exists():

            if st.button(
                f"Start {chapter['title']}",
                key=f"chapter_{chapter['id']}"
            ):
                st.session_state.chapter_started = True
                st.session_state.selected_chapter = chapter["id"]
                st.session_state.scene_index = 0
                st.session_state.quiz_submitted = False
                st.session_state.challenge_submitted = False
                st.session_state.activity_submitted = False
                st.session_state.experiment_result = None
                st.rerun()

        else:
            st.info("🚧 Coming Soon")

        st.divider()

# ─── Chapter Playback Mode ────────────────────────────────────────────────────

if st.session_state.chapter_started:

    # Compact top bar: Home button + Chapter title + XP
    col_home, col_title, col_xp_mini = st.columns([1, 4, 1])

    with col_home:
        if st.button("🏠 Home"):
            st.session_state.chapter_started = False
            st.session_state.scene_index = 0
            st.session_state.quiz_submitted = False
            st.session_state.challenge_submitted = False
            st.session_state.activity_submitted = False
            st.session_state.experiment_result = None
            st.rerun()

    with col_title:
        st.markdown("**🌟 WonderLearn**")

    with col_xp_mini:
        st.metric("⭐ XP", st.session_state.xp)

    # Load chapter data
    chapter_data = load_chapter(st.session_state.selected_chapter)
    scenes_data = load_scenes(st.session_state.selected_chapter)

    if chapter_data is None or scenes_data is None:
        st.warning("🚧 This adventure is under development.")
        st.stop()

    scene_count = len(scenes_data["scenes"])
    scene = scenes_data["scenes"][st.session_state.scene_index]
    scene_type = scene.get("scene_type", "story")

    # Scene type indicator
    type_labels = {
        "story": "📖 Story", "explore": "🔍 Explore", "experiment": "🧪 Experiment",
        "activity": "🎮 Activity", "challenge": "⚡ Challenge", "quiz": "📝 Quiz",
        "summary": "📋 Summary", "badge": "🏆 Badge"
    }
    st.caption(f"{type_labels.get(scene_type, '📖 Scene')} | {chapter_data['title']}")

    # Background (if any)
    bg = scene.get("background", "none")
    if bg != "none":
        background_file = f"assets/backgrounds/{bg}.jpg"
        if Path(background_file).exists():
            st.image(background_file, use_container_width=True)

    # ─── Scene Type: STORY ────────────────────────────────────────────────────

    if scene_type == "story":
        col_content, col_char = st.columns([3, 1])

        with col_content:
            st.header(scene["title"])

            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

            # Animation
            if "animation" in scene:
                render_animation(scene["animation"])

            # Steps display
            if "steps_display" in scene:
                st.write("")
                for i, step in enumerate(scene["steps_display"]):
                    st.markdown(f"""
                    <div class='step-card' style='animation-delay: {i * 0.2}s;'>
                        <strong>{step['icon']} Step {step['step']}: {step['title']}</strong><br>
                        {step['description']}
                    </div>
                    """, unsafe_allow_html=True)

            if "fun_fact" in scene:
                st.markdown(f"""
                <div class='fun-fact-box'>
                    <strong>🧠 Fun Fact:</strong> {scene['fun_fact']}
                </div>
                """, unsafe_allow_html=True)

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=250)

    # ─── Scene Type: EXPLORE ─────────────────────────────────────────────────

    elif scene_type == "explore":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        # Animation
        if "animation" in scene:
            render_animation(scene["animation"])

        st.write("")
        st.subheader("🔍 Explore — Click to Learn More")

        if "hotspots" in scene:
            for hotspot in scene["hotspots"]:
                with st.expander(f"{hotspot['icon']} {hotspot['name']}", expanded=False):
                    st.write(hotspot["description"])
                    if "examples" in hotspot:
                        examples_str = ", ".join(hotspot["examples"])
                        st.info(f"📌 Examples: {examples_str}")
                    if "fun_fact" in hotspot:
                        st.markdown(f"""
                        <div class='fun-fact-box'>
                            <strong>🧠 Fun Fact:</strong> {hotspot['fun_fact']}
                        </div>
                        """, unsafe_allow_html=True)

    # ─── Scene Type: EXPERIMENT ───────────────────────────────────────────────

    elif scene_type == "experiment":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "animation" in scene:
            render_animation(scene["animation"])

        if "experiment" in scene:
            exp = scene["experiment"]
            st.write("")
            st.subheader(f"🧪 {exp['title']}")
            st.write(exp["instructions"])

            if "steps" in exp:
                for step in exp["steps"]:
                    st.markdown(f"**{step['step_number']}.** {step['text']}")

            if "observation_question" in exp:
                st.write("")
                st.info(f"🔬 Observe: {exp['observation_question']}")
                user_obs = st.text_area("Your observation:", key=f"obs_{scene['id']}")
                if st.button("Check", key=f"exp_check_{scene['id']}"):
                    st.session_state.experiment_result = True
                    st.success(f"✅ Great observation! {exp.get('expected_result', '')}")

    # ─── Scene Type: ACTIVITY ─────────────────────────────────────────────────

    elif scene_type == "activity":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        # Animation
        if "animation" in scene:
            render_animation(scene["animation"])

        if "activity" in scene:
            activity = scene["activity"]
            st.write("")
            st.subheader(f"🎮 {activity['title']}")
            st.write(activity["instructions"])

            # ─── Matching Activity ────────────────────────────────────────────
            if activity["type"] == "matching":
                answers = {}
                options = activity["options"]

                for pair in activity["pairs"]:
                    answers[pair["item"]] = st.selectbox(
                        f"{pair['icon']} {pair['item']}",
                        options=["— Select —"] + options,
                        key=f"match_{scene['id']}_{pair['item']}"
                    )

                if st.button("✅ Check Answers", key=f"check_match_{scene['id']}"):
                    st.session_state.activity_submitted = True
                    correct = 0
                    for pair in activity["pairs"]:
                        if answers[pair["item"]] == pair["match"]:
                            correct += 1
                    st.session_state.activity_score = correct

                if st.session_state.activity_submitted:
                    total = len(activity["pairs"])
                    score = st.session_state.activity_score

                    if score == total:
                        st.balloons()
                        st.success(f"🎉 Perfect! You got all {total} correct!")
                    elif score >= total * 0.7:
                        st.success(f"👍 Great job! {score}/{total} correct!")
                    else:
                        st.warning(f"You got {score}/{total} correct. Review below:")

                    for pair in activity["pairs"]:
                        user_ans = answers.get(pair["item"], "— Select —")
                        is_correct = user_ans == pair["match"]
                        icon = "✅" if is_correct else "❌"
                        st.markdown(f"**{icon} {pair['item']}** → Correct: **{pair['match']}**")
                        if "explanation" in pair:
                            st.caption(f"   {pair['explanation']}")

            # ─── Sequence Activity ────────────────────────────────────────────
            elif activity["type"] == "sequence":
                st.write("Arrange these steps in the correct order (1 = first):")
                user_order = {}

                for step in activity["steps"]:
                    user_order[step["id"]] = st.selectbox(
                        f"{step['icon']} {step['name']}",
                        options=list(range(1, len(activity["steps"]) + 1)),
                        key=f"seq_{scene['id']}_{step['id']}"
                    )

                if st.button("✅ Check Order", key=f"check_seq_{scene['id']}"):
                    st.session_state.activity_submitted = True
                    correct = sum(
                        1 for step in activity["steps"]
                        if user_order[step["id"]] == step["correct_position"]
                    )
                    st.session_state.activity_score = correct

                if st.session_state.activity_submitted:
                    total = len(activity["steps"])
                    score = st.session_state.activity_score

                    if score == total:
                        st.balloons()
                        st.success(f"🎉 Perfect order! All {total} steps correct!")
                    elif score >= total * 0.7:
                        st.success(f"👍 Good effort! {score}/{total} in correct position!")
                    else:
                        st.warning(f"You got {score}/{total} correct. The correct order is:")
                        for step in sorted(activity["steps"], key=lambda x: x["correct_position"]):
                            st.markdown(f"**{step['correct_position']}.** {step['name']}")

    # ─── Scene Type: CHALLENGE ────────────────────────────────────────────────

    elif scene_type == "challenge":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "challenge" in scene:
            challenge = scene["challenge"]
            st.write("")
            st.subheader(f"⚡ {challenge['title']}")

            user_answers = {}
            for q in challenge["questions"]:
                user_answers[q["id"]] = st.radio(
                    f"**{q['statement']}**",
                    options=["True", "False"],
                    key=f"tf_{scene['id']}_{q['id']}",
                    horizontal=True
                )

            if st.button("✅ Submit Challenge", key=f"submit_challenge_{scene['id']}"):
                st.session_state.challenge_submitted = True
                correct = 0
                for q in challenge["questions"]:
                    user_bool = user_answers[q["id"]] == "True"
                    if user_bool == q["answer"]:
                        correct += 1
                st.session_state.challenge_score = correct

            if st.session_state.challenge_submitted:
                total = len(challenge["questions"])
                score = st.session_state.challenge_score

                if score == total:
                    st.balloons()
                    st.success(f"🎉 Perfect! All {total} correct!")
                elif score >= total * 0.7:
                    st.success(f"👍 Great! {score}/{total} correct!")
                else:
                    st.warning(f"You got {score}/{total}. Review:")

                for q in challenge["questions"]:
                    user_bool = user_answers[q["id"]] == "True"
                    is_correct = user_bool == q["answer"]
                    icon = "✅" if is_correct else "❌"
                    correct_str = "True" if q["answer"] else "False"
                    st.markdown(f"**{icon}** {q['statement']} → **{correct_str}**")
                    if "explanation" in q:
                        st.caption(f"   {q['explanation']}")

    # ─── Scene Type: QUIZ ─────────────────────────────────────────────────────

    elif scene_type == "quiz":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "quiz" in scene:
            quiz = scene["quiz"]
            st.write("")
            st.subheader(f"📝 {quiz['title']}")
            st.write(f"**Pass score: {quiz['pass_score']}/{len(quiz['questions'])}**")

            user_answers = {}
            for i, q in enumerate(quiz["questions"]):
                user_answers[q["id"]] = st.radio(
                    f"**Q{i+1}. {q['question']}**",
                    options=q["options"],
                    key=f"quiz_{scene['id']}_{q['id']}"
                )

            if st.button("📨 Submit Quiz", key=f"submit_quiz_{scene['id']}"):
                st.session_state.quiz_submitted = True
                correct = 0
                for q in quiz["questions"]:
                    correct_answer = q["options"][q["correct"]]
                    if user_answers[q["id"]] == correct_answer:
                        correct += 1
                st.session_state.quiz_score = correct

            if st.session_state.quiz_submitted:
                total = len(quiz["questions"])
                score = st.session_state.quiz_score
                passed = score >= quiz["pass_score"]

                if passed:
                    st.balloons()
                    st.success(f"🎉 Congratulations! You scored {score}/{total} — Quiz Passed!")
                else:
                    st.error(f"You scored {score}/{total}. You need {quiz['pass_score']} to pass. Review and try again!")

                st.write("---")
                st.write("**Review:**")
                for q in quiz["questions"]:
                    correct_answer = q["options"][q["correct"]]
                    user_ans = user_answers[q["id"]]
                    is_correct = user_ans == correct_answer
                    css_class = "quiz-correct" if is_correct else "quiz-wrong"
                    icon = "✅" if is_correct else "❌"
                    st.markdown(f"""
                    <div class='{css_class}'>
                        {icon} <strong>{q['question']}</strong><br>
                        Your answer: {user_ans} | Correct: <strong>{correct_answer}</strong><br>
                        <em>{q.get('explanation', '')}</em>
                    </div>
                    """, unsafe_allow_html=True)

    # ─── Scene Type: SUMMARY ──────────────────────────────────────────────────

    elif scene_type == "summary":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "summary_points" in scene:
            st.write("")
            st.subheader("📋 What You Learned")
            for i, point in enumerate(scene["summary_points"]):
                if isinstance(point, dict):
                    st.markdown(f"""
                    <div class='summary-card' style='animation-delay: {i * 0.15}s;'>
                        <strong>{point['icon']} {point['title']}</strong><br>
                        {point['text']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='summary-card' style='animation-delay: {i * 0.15}s;'>
                        <strong>{point}</strong>
                    </div>
                    """, unsafe_allow_html=True)

    # ─── Scene Type: BADGE ────────────────────────────────────────────────────

    elif scene_type == "badge":
        if "badge" in scene:
            badge = scene["badge"]

            st.markdown(f"""
            <div class='badge-container'>
                <div class='badge-icon'>{badge['icon']}</div>
                <h2>🏆 {badge['name']}</h2>
                <p>{badge['description']}</p>
            </div>
            """, unsafe_allow_html=True)

            if badge["name"] not in st.session_state.badges:
                st.session_state.badges.append(badge["name"])
                st.balloons()

        st.header(scene["title"])

        if "dialogue" in scene:
            st.markdown(f"""
            <div class='dialogue-box'>
                <div class='speaker'>{scene['dialogue']['speaker']}</div>
                <br>{scene['dialogue']['text']}
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # TTS audio
        if scene.get("tts"):
            with st.expander("🔊 Listen to Narration"):
                render_audio_player(scene["narration"], scene["id"])

    # ─── XP Award ─────────────────────────────────────────────────────────────

    if scene.get("xp") and f"xp_scene_{scene['id']}_ch{st.session_state.selected_chapter}" not in st.session_state:
        st.session_state.xp += scene["xp"]
        st.session_state[f"xp_scene_{scene['id']}_ch{st.session_state.selected_chapter}"] = True

    # ─── Navigation ───────────────────────────────────────────────────────────

    st.write("")
    st.write("")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

    with nav_col1:
        if st.session_state.scene_index > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.scene_index -= 1
                st.session_state.quiz_submitted = False
                st.session_state.challenge_submitted = False
                st.session_state.activity_submitted = False
                st.rerun()

    with nav_col2:
        st.markdown(
            f"<div style='text-align: center; color: #6B7280; padding: 10px;'>"
            f"Scene {st.session_state.scene_index + 1} of {scene_count}"
            f"</div>",
            unsafe_allow_html=True
        )

    with nav_col3:
        if st.session_state.scene_index < scene_count - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.scene_index += 1
                st.session_state.quiz_submitted = False
                st.session_state.challenge_submitted = False
                st.session_state.activity_submitted = False
                st.rerun()
        else:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.chapter_started = False
                st.session_state.scene_index = 0
                st.session_state.quiz_submitted = False
                st.rerun()

# ─── Footer ──────────────────────────────────────────────────────────────────

st.write("")
st.write("")

# ─── Footer ──────────────────────────────────────────────────────────────────

st.write("")
st.write("")
st.markdown("""
<div style='text-align: center; color: #9CA3AF; padding: 20px; font-size: 14px;'>
    WonderLearn © 2026 | Learn Through Stories, Explore Through Adventures
</div>
""", unsafe_allow_html=True)
