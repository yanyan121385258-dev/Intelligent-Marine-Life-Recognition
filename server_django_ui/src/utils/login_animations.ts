import { onUnmounted } from 'vue';

let bubblesAnimationId: number | null = null;
let oceanParticlesAnimationId: number | null = null;

export const initBubbles = () => {
  const canvas = document.getElementById('bubbles') as HTMLCanvasElement | null;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const bubbles: any[] = [];
  const bubbleCount = 30;

  for (let i = 0; i < bubbleCount; i++) {
    bubbles.push({
      x: Math.random() * canvas.width,
      y: canvas.height + Math.random() * 100,
      radius: Math.random() * 8 + 3,
      speed: Math.random() * 1.5 + 0.5,
      wobble: Math.random() * Math.PI * 2,
      wobbleSpeed: Math.random() * 0.02 + 0.01,
      wobbleAmount: Math.random() * 30 + 10,
      opacity: Math.random() * 0.5 + 0.3,
    });
  }

  const updateBubble = (bubble: any) => {
    bubble.y -= bubble.speed;
    bubble.wobble += bubble.wobbleSpeed;
    bubble.x += Math.sin(bubble.wobble) * 0.5;
    if (bubble.y + bubble.radius < 0) {
      bubble.y = canvas.height + bubble.radius;
      bubble.x = Math.random() * canvas.width;
    }
  };

  const drawBubble = (bubble: any) => {
    ctx.beginPath();
    const gradient = ctx.createRadialGradient(
      bubble.x - bubble.radius * 0.3,
      bubble.y - bubble.radius * 0.3,
      0,
      bubble.x,
      bubble.y,
      bubble.radius
    );
    gradient.addColorStop(0, `rgba(200, 240, 255, ${bubble.opacity})`);
    gradient.addColorStop(0.5, `rgba(100, 200, 255, ${bubble.opacity * 0.6})`);
    gradient.addColorStop(1, `rgba(50, 150, 255, ${bubble.opacity * 0.3})`);
    ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(
      bubble.x - bubble.radius * 0.3,
      bubble.y - bubble.radius * 0.3,
      bubble.radius * 0.2,
      0,
      Math.PI * 2
    );
    ctx.fillStyle = `rgba(255, 255, 255, ${bubble.opacity * 0.8})`;
    ctx.fill();
  };

  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    bubbles.forEach((bubble) => {
      updateBubble(bubble);
      drawBubble(bubble);
    });
    bubblesAnimationId = requestAnimationFrame(animate);
  };

  animate();

  const handleResize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };

  window.addEventListener('resize', handleResize);

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (bubblesAnimationId) {
      cancelAnimationFrame(bubblesAnimationId);
    }
  });
};

export const initOceanParticles = () => {
  const canvas = document.getElementById('oceanParticles') as HTMLCanvasElement | null;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles: any[] = [];
  const particleCount = 50;
  const colors = ['#00d4ff', '#00b4d8', '#48cae4', '#90e0ef', '#ade8f4'];

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 3 + 1,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: Math.random() * 0.6 + 0.2,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: Math.random() * 0.03 + 0.01,
    });
  }

  const updateParticle = (particle: any) => {
    particle.x += particle.vx;
    particle.y += particle.vy;
    particle.pulse += particle.pulseSpeed;
    if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
    if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
  };

  const drawParticle = (particle: any) => {
    const pulseRadius = particle.radius * (1 + Math.sin(particle.pulse) * 0.3);
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, pulseRadius, 0, Math.PI * 2);
    ctx.fillStyle = particle.color;
    ctx.globalAlpha = particle.alpha * (0.7 + Math.sin(particle.pulse) * 0.3);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, pulseRadius * 2, 0, Math.PI * 2);
    const gradient = ctx.createRadialGradient(
      particle.x,
      particle.y,
      0,
      particle.x,
      particle.y,
      pulseRadius * 2
    );
    gradient.addColorStop(0, `rgba(0, 212, 255, ${particle.alpha * 0.3})`);
    gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');
    ctx.fillStyle = gradient;
    ctx.fill();
  };

  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach((particle) => {
      updateParticle(particle);
      drawParticle(particle);
    });
    oceanParticlesAnimationId = requestAnimationFrame(animate);
  };

  animate();

  const handleResize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };

  window.addEventListener('resize', handleResize);

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (oceanParticlesAnimationId) {
      cancelAnimationFrame(oceanParticlesAnimationId);
    }
  });
};
