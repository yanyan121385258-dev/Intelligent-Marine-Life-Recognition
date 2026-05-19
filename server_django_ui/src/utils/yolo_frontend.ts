// 前端ONNX YOLO检测工具类
import * as ort from 'onnxruntime-web';

// ONNX检测结果接口
export interface YOLODetectionResult {
  detections: Array<{
    class_name: string;
    confidence: number;
    bbox: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  }>;
  object_count: number;
  detected_categories: string[];
  confidence_scores: number[];
  avg_confidence: number;
  annotated_image: string; // base64图像
  processing_time: number;
}

// 不预置任何类别名称；等待后端或标签文件提供

class YOLODetector {
  private session: ort.InferenceSession | null = null;
  private modelPath: string = '';
  private classNames: string[] = [];
  private inputShape: [number, number] = [640, 640]; // 默认输入尺寸（可在 WASM 下动态调小）
  private currentEP: 'webgpu' | 'webgl' | 'wasm' = 'wasm';

  /**
   * 加载ONNX模型
   * @param modelPath 模型路径（相对于public目录）
   * @param classNames 类别名称列表（可选，如果不提供则使用默认COCO类别）
   */
  async loadModel(
    modelPath: string,
    classNames?: string[],
    forceEP?: 'webgpu' | 'webgl' | 'wasm'
  ): Promise<void> {
    try {
      console.log('🔄 开始加载ONNX模型:', modelPath);

      // 设置类别名称
      if (classNames && classNames.length > 0) {
        this.classNames = classNames;
        console.log('📦 使用自定义类别:', classNames.length, '个类别');
      } else {
        // 如果未提供类别，稍后根据输出维度自动推断数量并用 class_0.. 命名
        this.classNames = [];
        console.log('📦 未提供类别，将根据模型输出自动推断类别数量');
      }

      // 动态选择可用的 wasm 资源路径，避免 404/HTML 导致的“magic word”错误
      const ensureWasmPath = async () => {
        const candidates = [
          'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.23.2/dist/',
          'https://unpkg.com/onnxruntime-web@1.23.2/dist/',
          '/onnxruntime-web/', // 如果你把 dist 拷贝到 public/onnxruntime-web/
          '/ort/', // 或者 public/ort/
        ];
        for (const base of candidates) {
          try {
            const testUrl = base.replace(/\/$/, '') + '/ort-wasm.wasm';
            const res = await fetch(testUrl, {
              method: 'HEAD',
              cache: 'no-store',
              mode: 'no-cors' as any,
            });
            // no-cors 模式下 status 为 0，也视为可用（跨域但可下载）
            if (res.ok || res.status === 0) {
              // @ts-ignore
              ort.env.wasm.wasmPaths = base;
              return true;
            }
          } catch {}
        }
        return false;
      };

      await ensureWasmPath();

      // 配置 WASM 线程：若不支持跨域隔离/SharedArrayBuffer，则退回单线程，避免“worker not ready”
      const canMultiThread =
        (self as any).crossOriginIsolated && typeof (self as any).SharedArrayBuffer !== 'undefined';
      try {
        // @ts-ignore
        ort.env.wasm.numThreads = canMultiThread
          ? Math.max(2, Math.min(4, (navigator as any)?.hardwareConcurrency || 2))
          : 1;
        // @ts-ignore
        ort.env.wasm.proxy = true;
      } catch {}

      const createWithEP = async (ep: 'webgpu' | 'webgl' | 'wasm') => {
        if (ep === 'webgpu') {
          const prefer: ort.InferenceSession.SessionOptions = {
            executionProviders: ['webgpu'],
            graphOptimizationLevel: 'all',
          };
          this.session = await ort.InferenceSession.create(modelPath, prefer);
          this.currentEP = 'webgpu';
          return;
        }
        if (ep === 'webgl') {
          const prefer: ort.InferenceSession.SessionOptions = {
            executionProviders: ['webgl'],
            graphOptimizationLevel: 'all',
          };
          this.session = await ort.InferenceSession.create(modelPath, prefer);
          this.currentEP = 'webgl';
          return;
        }
        // wasm
        const prefer: ort.InferenceSession.SessionOptions = {
          executionProviders: ['wasm'],
          graphOptimizationLevel: 'all',
        };
        this.session = await ort.InferenceSession.create(modelPath, prefer);
        this.currentEP = 'wasm';
      };

      // 配置 ONNX Runtime：优先 GPU（WebGPU/WebGL），再回退 WASM
      // 支持通过 localStorage 开关强制使用 WASM：localStorage.setItem('ort_force_wasm','1')
      // 也可通过第三个参数 forceEP 指定（用于错误时的程序化降级）
      const forceWasm = forceEP === 'wasm' || localStorage.getItem('ort_force_wasm') === '1';
      // 1) WebGPU（实验性，浏览器需支持 navigator.gpu）
      let created = false;
      if (!forceWasm && (navigator as any)?.gpu && (!forceEP || forceEP === 'webgpu')) {
        try {
          // 动态引入 webgpu 版本（若不支持不会打包）
          await import('onnxruntime-web/webgpu');
          await createWithEP('webgpu');
          created = true;
          console.log('✅ 使用 WebGPU 推理');
        } catch (e) {
          console.warn('⚠️ WebGPU 初始化失败，回退到 WebGL:', e);
        }
      }

      // 2) WebGL（GPU 加速，兼容更好）
      if (!forceWasm && !created && (!forceEP || forceEP === 'webgl')) {
        try {
          await createWithEP('webgl');
          created = true;
          console.log('✅ 使用 WebGL 推理');
        } catch (e2) {
          console.warn('⚠️ WebGL 初始化失败，回退到 WASM:', e2);
        }
      }

      // 3) WASM（CPU）
      if (!created) {
        try {
          // 设置 WASM 线程/特性（路径已在 ensureWasmPath 中选择）
          // @ts-ignore
          ort.env.wasm.numThreads = Math.max(
            1,
            Math.min(4, (navigator as any)?.hardwareConcurrency || 2)
          );
          // @ts-ignore
          ort.env.wasm.proxy = true;
        } catch {}

        await createWithEP('wasm');
        console.log('✅ 使用 WASM 推理');
      }
      this.modelPath = modelPath;

      // 根据后端动态调整输入尺寸：WASM 默认调小以提升流畅度，可用 localStorage 覆盖
      try {
        const override = parseInt(localStorage.getItem('ort_input_size') || '', 10);
        if (Number.isFinite(override) && override >= 256 && override <= 1024) {
          this.inputShape = [override, override] as any;
        } else if (this.currentEP === 'wasm') {
          this.inputShape = [512, 512] as any;
        } else {
          this.inputShape = [640, 640] as any;
        }
        console.log('🧩 推理输入尺寸:', this.inputShape[0]);
      } catch {}

      // 获取模型输入输出信息（兼容性更强的写法）
      const inputNames = this.session.inputNames;
      const outputNames = this.session.outputNames;
      console.log('✅ 模型加载成功');
      console.log('📥 输入:', inputNames);
      console.log('📤 输出:', outputNames);

      // 尝试从 outputMetadata 推断类别数（某些环境不提供 dims，需要兜底）
      try {
        if (outputNames && outputNames.length > 0) {
          const outputMetadata: any = (this.session as any).outputMetadata;
          const outputName = outputNames[0];
          const meta = outputMetadata?.[outputName];
          const outputShape: number[] | undefined = meta?.dims;
          if (Array.isArray(outputShape) && outputShape.length >= 3) {
            const numClasses = (outputShape[2] as number) - 5; // YOLO: [N, B, 5+C]
            if (
              Number.isFinite(numClasses) &&
              numClasses > 0 &&
              numClasses !== this.classNames.length
            ) {
              console.warn(
                `⚠️ 模型输出类别数 (${numClasses}) 与提供的类别数 (${this.classNames.length}) 不匹配/或未提供`
              );
              if (this.classNames.length === 0) {
                this.classNames = Array.from({ length: numClasses }, (_, i) => `class_${i}`);
                console.log('📦 根据模型输出调整类别数量为:', numClasses);
              }
            }
          } else {
            console.warn(
              '⚠️ 无法从 outputMetadata 推断输出维度，将在首次推理时根据输出tensor推断。'
            );
          }
        }
      } catch (metaErr) {
        console.warn('⚠️ 读取 outputMetadata 失败，将在首次推理时推断类别数。', metaErr);
      }
    } catch (error) {
      console.error('❌ 加载模型失败:', error);
      throw new Error(`加载ONNX模型失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 检查模型是否已加载
   */
  isLoaded(): boolean {
    return this.session !== null;
  }

  /**
   * 获取当前加载的模型路径
   */
  getModelPath(): string {
    return this.modelPath;
  }

  /**
   * 获取类别名称列表
   */
  getClassNames(): string[] {
    return this.classNames;
  }

  /**
   * 预处理图像（Ultralytics letterbox：保比例缩放+灰边填充）
   * 返回输入张量与还原坐标所需的比例与padding
   */
  private preprocessImage(image: HTMLImageElement | HTMLVideoElement | HTMLCanvasElement): {
    input: Float32Array;
    ratio: number;
    padX: number;
    padY: number;
    dstW: number;
    dstH: number;
    srcW: number;
    srcH: number;
  } {
    const dstW = this.inputShape[0];
    const dstH = this.inputShape[1];
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('无法创建canvas上下文');

    const srcW =
      image instanceof HTMLVideoElement
        ? image.videoWidth
        : (image as HTMLImageElement | HTMLCanvasElement).width;
    const srcH =
      image instanceof HTMLVideoElement
        ? image.videoHeight
        : (image as HTMLImageElement | HTMLCanvasElement).height;

    // 计算 letterbox
    const r = Math.min(dstW / srcW, dstH / srcH);
    const newW = Math.round(srcW * r);
    const newH = Math.round(srcH * r);
    const padX = Math.floor((dstW - newW) / 2);
    const padY = Math.floor((dstH - newH) / 2);

    canvas.width = dstW;
    canvas.height = dstH;
    // 背景填充灰色(114)与 Ultralytics 一致
    ctx.fillStyle = 'rgb(114,114,114)';
    ctx.fillRect(0, 0, dstW, dstH);
    // 绘制等比缩放后的图像到中间
    ctx.drawImage(image as any, 0, 0, srcW, srcH, padX, padY, newW, newH);

    const imageData = ctx.getImageData(0, 0, dstW, dstH);
    const data = imageData.data;

    const input = new Float32Array(3 * dstW * dstH);
    for (let i = 0; i < data.length; i += 4) {
      const r8 = data[i] / 255.0;
      const g8 = data[i + 1] / 255.0;
      const b8 = data[i + 2] / 255.0;
      const idx = i / 4;
      input[idx] = r8;
      input[idx + dstW * dstH] = g8;
      input[idx + dstW * dstH * 2] = b8;
    }

    return { input, ratio: r, padX, padY, dstW, dstH, srcW, srcH };
  }

  /**
   * 非极大值抑制（NMS）
   */
  private nms(
    boxes: Array<{ x: number; y: number; w: number; h: number; conf: number; class: number }>,
    iouThreshold: number
  ): number[] {
    if (boxes.length === 0) return [];

    // 按置信度排序
    boxes.sort((a, b) => b.conf - a.conf);

    const selected: number[] = [];
    const suppressed = new Set<number>();

    for (let i = 0; i < boxes.length; i++) {
      if (suppressed.has(i)) continue;

      selected.push(i);
      const box1 = boxes[i];

      for (let j = i + 1; j < boxes.length; j++) {
        if (suppressed.has(j)) continue;

        const box2 = boxes[j];

        // 计算IoU
        const iou = this.calculateIoU(box1, box2);

        if (iou > iouThreshold) {
          suppressed.add(j);
        }
      }
    }

    return selected;
  }

  /**
   * 计算IoU（交并比）
   */
  private calculateIoU(
    box1: { x: number; y: number; w: number; h: number },
    box2: { x: number; y: number; w: number; h: number }
  ): number {
    const x1 = Math.max(box1.x, box2.x);
    const y1 = Math.max(box1.y, box2.y);
    const x2 = Math.min(box1.x + box1.w, box2.x + box2.w);
    const y2 = Math.min(box1.y + box1.h, box2.y + box2.h);

    if (x2 < x1 || y2 < y1) return 0;

    const intersection = (x2 - x1) * (y2 - y1);
    const area1 = box1.w * box1.h;
    const area2 = box2.w * box2.h;
    const union = area1 + area2 - intersection;

    return intersection / union;
  }

  /**
   * 后处理检测结果
   */
  private postprocess(
    output: ort.Tensor,
    meta: { ratio: number; padX: number; padY: number; srcW: number; srcH: number },
    confThreshold: number,
    nmsThreshold: number,
    opts?: { maxDetections?: number; minBoxArea?: number; classWise?: boolean }
  ): Array<{
    class_name: string;
    confidence: number;
    bbox: { x: number; y: number; width: number; height: number };
  }> {
    const outputData = output.data as Float32Array;
    const outputShape = output.dims || [];

    // YOLO输出常见两种：
    //  A) [1, num_boxes, 5+num_classes]
    //  B) [1, 5+num_classes, num_boxes]
    // 另外也可能已经扁平化为 [num_boxes, 5+num_classes]
    let numBoxes = 0;
    let numFeatures = 0;
    if (outputShape.length === 3) {
      // 取更大的作为 boxes 维度（通常是 8400），较小的是 5+C（通常是 85）
      const a = outputShape[1] as number;
      const b = outputShape[2] as number;
      if (a >= b) {
        numBoxes = a;
        numFeatures = b;
      } else {
        numBoxes = b;
        numFeatures = a;
      }
    } else if (outputShape.length === 2) {
      numBoxes = outputShape[0] as number;
      numFeatures = outputShape[1] as number;
    } else {
      // 无维度信息时根据长度推断（保底）
      numFeatures = 85;
      numBoxes = Math.floor(outputData.length / numFeatures);
    }
    const numClasses = Math.max(0, numFeatures - 5);

    const detections: Array<{
      x: number;
      y: number;
      w: number;
      h: number;
      conf: number;
      class: number;
    }> = [];

    // 还原到原图坐标：先减去 padding，再除以 ratio
    const { ratio, padX, padY, srcW: originalWidth, srcH: originalHeight } = meta;

    // 获取 (row i, col j) 的值，兼容布局 A/B
    const getVal = (i: number, j: number): number => {
      if (outputShape.length === 3) {
        const a = outputShape[1] as number;
        const b = outputShape[2] as number;
        if (a >= b) {
          // [1, boxes, features]
          return outputData[i * b + j];
        }
        // [1, features, boxes]
        return outputData[j * a + i];
      }
      // [boxes, features]
      return outputData[i * numFeatures + j];
    };

    // sigmoid
    const sigmoid = (v: number) => 1 / (1 + Math.exp(-v));

    // 情况一：部分导出的ONNX已经做过NMS，输出形如 [num, 6]：x1,y1,x2,y2,score,classId（或其它顺序）。
    const tryPostNmsLayouts = () => {
      const candidates: Array<
        (
          row: (j: number) => number
        ) => { x: number; y: number; w: number; h: number; conf: number; cls: number } | null
      > = [
        // [x1,y1,x2,y2,score,cls]
        (get) => {
          const x1 = get(0),
            y1 = get(1),
            x2 = get(2),
            y2 = get(3);
          const score = get(4),
            cls = get(5);
          if (!isFinite(x1 + y1 + x2 + y2 + score + cls)) return null;
          if (score < 0 || score > 1) return null;
          const w = Math.abs(x2 - x1),
            h = Math.abs(y2 - y1);
          return {
            x: Math.min(x1, x2),
            y: Math.min(y1, y2),
            w,
            h,
            conf: score,
            cls: Math.max(0, Math.floor(cls)),
          };
        },
        // [cls,score,x1,y1,x2,y2]
        (get) => {
          const cls = get(0),
            score = get(1),
            x1 = get(2),
            y1 = get(3),
            x2 = get(4),
            y2 = get(5);
          if (!isFinite(x1 + y1 + x2 + y2 + score + cls)) return null;
          if (score < 0 || score > 1) return null;
          const w = Math.abs(x2 - x1),
            h = Math.abs(y2 - y1);
          return {
            x: Math.min(x1, x2),
            y: Math.min(y1, y2),
            w,
            h,
            conf: score,
            cls: Math.max(0, Math.floor(cls)),
          };
        },
        // [x,y,w,h,score,cls]（xywh）
        (get) => {
          const x = get(0),
            y = get(1),
            w = get(2),
            h = get(3),
            score = get(4),
            cls = get(5);
          if (!isFinite(x + y + w + h + score + cls)) return null;
          if (score < 0 || score > 1) return null;
          return {
            x: x - w / 2,
            y: y - h / 2,
            w,
            h,
            conf: score,
            cls: Math.max(0, Math.floor(cls)),
          };
        },
      ];
      const out: typeof detections = [];
      for (let i = 0; i < numBoxes; i++) {
        const getter = (j: number) => getVal(i, j);
        let picked = null;
        for (const decode of candidates) {
          picked = decode(getter);
          if (picked && picked.conf >= confThreshold) break;
        }
        if (!picked || picked.conf < confThreshold) continue;
        // 还原坐标
        let { x, y, w, h, conf, cls } = picked;
        x = (x - padX) / ratio;
        y = (y - padY) / ratio;
        w = w / ratio;
        h = h / ratio;
        const area = Math.max(0, w) * Math.max(0, h);
        const minArea = opts?.minBoxArea ?? meta.srcW * meta.srcH * 0.0001;
        if (area <= 0 || area < minArea) continue;
        out.push({ x, y, w, h, conf, class: cls });
      }
      return out;
    };

    // 情况二：原始预测 [*, *, 5+num_classes]，需要 obj × class 计算。
    // 支持两种坐标格式：xywh(中心点) 与 xyxy(左上/右下)。优先取能得到更多有效框的解码。
    const decode = (mode: 'xywh' | 'xyxy') => {
      const out: typeof detections = [];
      for (let i = 0; i < numBoxes; i++) {
        const v0 = getVal(i, 0);
        const v1 = getVal(i, 1);
        const v2 = getVal(i, 2);
        const v3 = getVal(i, 3);
        const objConf = sigmoid(getVal(i, 4));

        // 最大类别
        let maxClassConf = 0;
        let maxClassIdx = 0;
        for (let j = 0; j < numClasses; j++) {
          const classConf = sigmoid(getVal(i, 5 + j));
          if (classConf > maxClassConf) {
            maxClassConf = classConf;
            maxClassIdx = j;
          }
        }
        const confidence = objConf * maxClassConf;
        if (confidence < confThreshold) continue;

        let x = 0,
          y = 0,
          w = 0,
          h = 0;
        if (mode === 'xywh') {
          const xc = (v0 - padX) / ratio;
          const yc = (v1 - padY) / ratio;
          const wv = v2 / ratio;
          const hv = v3 / ratio;
          x = xc - wv / 2;
          y = yc - hv / 2;
          w = wv;
          h = hv;
        } else {
          // xyxy
          const x1 = (v0 - padX) / ratio;
          const y1 = (v1 - padY) / ratio;
          const x2 = (v2 - padX) / ratio;
          const y2 = (v3 - padY) / ratio;
          x = Math.min(x1, x2);
          y = Math.min(y1, y2);
          w = Math.abs(x2 - x1);
          h = Math.abs(y2 - y1);
        }
        const area = Math.max(0, w) * Math.max(0, h);
        const minArea = opts?.minBoxArea ?? originalWidth * originalHeight * 0.00005; // 放宽：0.005%
        if (area <= 0 || area < minArea) continue;
        if (w > 4 * originalWidth || h > 4 * originalHeight) continue; // 明显异常

        out.push({ x, y, w, h, conf: confidence, class: maxClassIdx });
      }
      return out;
    };

    let pick: typeof detections = [];
    // 若特征维很小（<=6），优先按“已NMS格式”解析
    if (numFeatures <= 6) {
      pick = tryPostNmsLayouts();
    }
    // 否则按原始格式解码
    if (pick.length === 0) {
      const d1 = decode('xywh');
      const d2 = decode('xyxy');
      pick = d2.length > d1.length ? d2 : d1;
    }
    detections.push(...pick);
    // 执行NMS（支持按类别）
    const classWise = opts?.classWise ?? true;
    let kept: Array<{ x: number; y: number; w: number; h: number; conf: number; class: number }> =
      [];
    if (classWise) {
      const byClass: Record<number, typeof detections> = {};
      for (const d of detections) {
        (byClass[d.class] ||= []).push(d);
      }
      for (const k in byClass) {
        const group = byClass[k];
        const idxs = this.nms(group, nmsThreshold);
        kept.push(...idxs.map((i) => group[i]));
      }
    } else {
      const idxs = this.nms(detections, nmsThreshold);
      kept = idxs.map((i) => detections[i]);
    }

    // 置信度排序并限制最大数量
    kept.sort((a, b) => b.conf - a.conf);
    const limited = kept.slice(0, opts?.maxDetections ?? 100);

    // 构建最终结果
    return limited.map((det) => {
      const className = this.classNames[det.class] || `class_${det.class}`;
      return {
        class_name: className,
        confidence: det.conf,
        bbox: {
          x: Math.max(0, det.x),
          y: Math.max(0, det.y),
          width: Math.min(det.w, originalWidth - det.x),
          height: Math.min(det.h, originalHeight - det.y),
        },
      };
    });
  }

  /**
   * 在图像上绘制检测框
   */
  private drawDetections(
    canvas: HTMLCanvasElement,
    detections: Array<{
      class_name: string;
      confidence: number;
      bbox: { x: number; y: number; width: number; height: number };
    }>
  ): void {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 为每个类别分配颜色
    const colors: { [key: string]: string } = {};
    const colorPalette = [
      '#FF6B6B',
      '#4ECDC4',
      '#45B7D1',
      '#FFA07A',
      '#98D8C8',
      '#F7DC6F',
      '#BB8FCE',
      '#85C1E2',
    ];

    detections.forEach((det, idx) => {
      if (!colors[det.class_name]) {
        colors[det.class_name] = colorPalette[idx % colorPalette.length];
      }
    });

    detections.forEach((det) => {
      const { x, y, width, height } = det.bbox;
      const color = colors[det.class_name];

      // 绘制边界框
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);

      // 绘制标签背景
      const label = `${det.class_name} ${(det.confidence * 100).toFixed(1)}%`;
      ctx.font = '14px Arial';
      const textMetrics = ctx.measureText(label);
      const textWidth = textMetrics.width;
      const textHeight = 20;

      ctx.fillStyle = color;
      ctx.fillRect(x, y - textHeight, textWidth + 10, textHeight);

      // 绘制标签文字
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(label, x + 5, y - 5);
    });
  }

  /**
   * 执行检测
   * @param image 图像元素（Image, Video, 或 Canvas）
   * @param confidenceThreshold 置信度阈值
   * @param nmsThreshold NMS阈值
   */
  async detect(
    image: HTMLImageElement | HTMLVideoElement | HTMLCanvasElement,
    confidenceThreshold: number = 0.25,
    nmsThreshold: number = 0.7
  ): Promise<YOLODetectionResult> {
    if (!this.session) {
      throw new Error('模型未加载，请先调用 loadModel()');
    }

    const startTime = performance.now();

    try {
      // 获取原始图像尺寸
      const originalWidth = image instanceof HTMLVideoElement ? image.videoWidth : image.width;
      const originalHeight = image instanceof HTMLVideoElement ? image.videoHeight : image.height;

      // 预处理图像（letterbox）
      const prep = this.preprocessImage(image);

      // 创建输入tensor [1, 3, H, W]
      const inputTensor = new ort.Tensor('float32', prep.input, [
        1,
        3,
        this.inputShape[1],
        this.inputShape[0],
      ]);

      // 执行推理
      const inputName = this.session.inputNames[0];
      const feeds = { [inputName]: inputTensor };
      const results = await this.session.run(feeds);

      // 获取输出
      const outputName = this.session.outputNames[0];
      const output = results[outputName];

      // 后处理
      const detections = this.postprocess(
        output,
        {
          ratio: prep.ratio,
          padX: prep.padX,
          padY: prep.padY,
          srcW: originalWidth,
          srcH: originalHeight,
        },
        confidenceThreshold,
        nmsThreshold,
        { maxDetections: 100, minBoxArea: originalWidth * originalHeight * 0.0001, classWise: true }
      );

      // 计算统计信息
      const objectCount = detections.length;
      const detectedCategories = [...new Set(detections.map((d) => d.class_name))];
      const confidenceScores = detections.map((d) => d.confidence);
      const avgConfidence =
        confidenceScores.length > 0
          ? confidenceScores.reduce((a, b) => a + b, 0) / confidenceScores.length
          : 0;

      // 绘制检测结果
      const canvas = document.createElement('canvas');
      canvas.width = originalWidth;
      canvas.height = originalHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(image, 0, 0, originalWidth, originalHeight);
        this.drawDetections(canvas, detections);
      }

      // 转换为base64（降低质量，减少内存与传输开销）
      const annotatedImage = canvas.toDataURL('image/jpeg', 0.4);

      const processingTime = (performance.now() - startTime) / 1000;

      return {
        detections: detections.map((d) => ({
          class_name: d.class_name,
          confidence: d.confidence,
          bbox: d.bbox,
        })),
        object_count: objectCount,
        detected_categories: detectedCategories,
        confidence_scores: confidenceScores,
        avg_confidence: avgConfidence,
        annotated_image: annotatedImage,
        processing_time: processingTime,
      };
    } catch (error) {
      console.error('❌ 检测失败:', error);
      // 若 GPU 后端不支持某些算子，自动回退到 WASM 并重试一次
      const msg = String((error as any)?.message || error);
      const needFallback =
        /GatherND|Unsupported data type|JSF Kernel|ExecuteKernel|WebGPU|WebGL|worker not ready/i.test(
          msg
        );
      if (needFallback && this.currentEP !== 'wasm') {
        try {
          console.warn('⚠️ 检测算子不被 GPU 支持，自动回退到 WASM 并重试一次。');
          // 强制全局与本次调用走 WASM
          localStorage.setItem('ort_force_wasm', '1');
          await this.loadModel(this.modelPath, this.classNames, 'wasm');
          // 强制使用 wasm
          // @ts-ignore
          ort.env.wasm.proxy = true;
          this.currentEP = 'wasm';
          return await this.detect(image, confidenceThreshold, nmsThreshold);
        } catch (e2) {
          console.error('❌ 回退到 WASM 后仍失败:', e2);
        }
      }
      // 如果已是 wasm，但报 worker not ready，再降级为单线程重建 session
      if (/worker not ready/i.test(msg) && this.currentEP === 'wasm') {
        try {
          // @ts-ignore
          ort.env.wasm.numThreads = 1;
          await this.loadModel(this.modelPath, this.classNames);
          return await this.detect(image, confidenceThreshold, nmsThreshold);
        } catch (e3) {
          console.error('❌ 降级单线程后仍失败:', e3);
        }
      }
      throw new Error(`检测失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 释放模型资源
   */
  dispose(): void {
    if (this.session) {
      // ONNX Runtime会自动管理资源，但我们可以清理引用
      this.session = null;
      this.modelPath = '';
      console.log('🗑️ 模型资源已释放');
    }
  }
}

// 导出单例
export const yoloDetector = new YOLODetector();
