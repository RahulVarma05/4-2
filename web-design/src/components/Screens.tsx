import React, { useState, useRef, useEffect } from "react";
import { motion } from "motion/react";
import { Play, ArrowRight, Zap, Layers, Cpu, Upload, Image as ImageIcon, FileVideo, CheckCircle2 } from "lucide-react";
import { Screen } from "./Shared";

interface ScreenProps {
  onNavigate: (screen: Screen) => void;
  isLoggedIn?: boolean;
  onLogin?: () => void;
}

export function LandingPage({ onNavigate, isLoggedIn }: ScreenProps) {
  const [showDemo, setShowDemo] = useState(false);

  return (
    <div className="pt-32 pb-24">
      <div className="max-w-[1440px] mx-auto px-6 md:px-12">
        {/* Hero Section */}
        <section className="text-center mb-32">


          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 bg-surface-container-low rounded-full text-[10px] font-black tracking-[0.2em] uppercase text-accent mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            MM.0 Now Live
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl font-black tracking-tighter leading-[0.9] text-on-surface uppercase mb-8"
          >
            Transfer Motion <br />
            <span className="text-accent italic">to any</span> Image
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="max-w-2xl mx-auto text-on-surface-variant text-lg mb-12 leading-relaxed"
          >
            Unlock professional-grade 3D motion transfer using advanced neural architectures.
            Transform static photography into fluid, kinetic experiences with clinical precision and zero manual keyframing.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
          >
            <button
              onClick={() => onNavigate("generate")}
              className="mimic-gradient text-on-primary px-10 py-5 rounded-full font-bold text-lg shadow-xl shadow-primary/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-3 group"
            >
              Try Now
              <Zap className="w-5 h-5 fill-current" />
            </button>
            <button
              onClick={() => setShowDemo(true)}
              className="bg-stone-200 text-stone-900 px-10 py-5 rounded-full font-bold text-lg hover:bg-stone-300 transition-colors"
            >
              Watch Demo
            </button>
          </motion.div>
        </section>

        {/* Feature Grid - Asymmetrical */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-32">
          <div className="lg:col-span-8">
            <div className="relative aspect-square md:aspect-video rounded-3xl overflow-hidden shadow-2xl group">
              <video
                src="samples/VideoProject.mp4"
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-full object-cover"
              />
            </div>
          </div>
          <div className="lg:col-span-4 flex flex-col gap-8">
            <div className="bg-surface-container-lowest p-6 rounded-3xl shadow-xl">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-6">
                <Cpu className="w-5 h-5" />
              </div>
              <div className="inline-block px-3 py-1 bg-primary/10 text-primary text-[10px] font-black uppercase tracking-widest rounded-full mb-4">Live</div>
              <h4 className="text-xl font-bold mb-4 uppercase tracking-tight">Neural Keypoint Detection</h4>
              <p className="text-on-surface-variant text-xs leading-relaxed">
                Real-time skeleton extraction from any source video with 99.8% point accuracy.
              </p>
            </div>
            <div className="bg-surface-container-lowest p-6 rounded-3xl shadow-xl">
              <div className="w-10 h-10 bg-accent/10 rounded-xl flex items-center justify-center text-accent mb-6">
                <Zap className="w-5 h-5" />
              </div>
              <h4 className="text-xl font-bold mb-4 uppercase tracking-tight">
                Real-Time Processing
              </h4>
              <p className="text-on-surface-variant text-xs leading-relaxed">
                GPU-accelerated rendering pipeline processes frames in under 50ms each.
              </p>
            </div>
          </div>
        </section>

        {/* Tech Stack Section */}
        <section className="flex flex-col lg:flex-row items-center gap-20 mb-32">
          <div className="w-full lg:w-1/2">
            <div className="relative">
              <div className="absolute -inset-10 bg-primary/5 rounded-full blur-3xl" />
              <img
                src="https://picsum.photos/seed/abstract/800/800"
                alt="Precision"
                className="relative w-full aspect-square object-cover rounded-3xl shadow-2xl"
                referrerPolicy="no-referrer"
              />
            </div>
          </div>
          <div className="w-full lg:w-1/2">
            <p className="text-primary font-black uppercase tracking-[0.2em] text-xs mb-6">The Tech Stack</p>
            <h2 className="text-4xl md:text-6xl font-black tracking-tighter leading-[0.95] uppercase mb-12">
              Precision in every frame. <br />
              Editorial in every pixel.
            </h2>

            <div className="space-y-12">
              <div className="flex gap-6">
                <span className="text-3xl font-black text-primary/20">01</span>
                <div>
                  <h4 className="text-xl font-bold uppercase tracking-tight mb-3">Optical Flow Synthesis</h4>
                  <p className="text-on-surface-variant leading-relaxed">
                    Our proprietary algorithm analyzes sub-pixel movement to ensure that motion isn't just copied, but naturally re-synthesized for the target image structure.
                  </p>
                </div>
              </div>
              <div className="flex gap-6">
                <span className="text-3xl font-black text-primary/20">02</span>
                <div>
                  <h4 className="text-xl font-bold uppercase tracking-tight mb-3">Latent Space Decoupling</h4>
                  <p className="text-on-surface-variant leading-relaxed">
                    Separate style from motion. Transfer the energy of a dance without losing the unique texture and identity of your original artwork.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-stone-950 rounded-[3rem] p-12 md:p-24 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,#0050d4,transparent_70%)]" />
          </div>
          <div className="relative z-10">
            <h2 className="text-4xl md:text-7xl font-black text-white uppercase tracking-tighter mb-8">
              Ready to animate your vision?
            </h2>
            <button
              onClick={() => onNavigate("generate")}
              className="bg-white text-stone-950 px-12 py-6 rounded-full font-bold text-xl hover:bg-stone-200 transition-all active:scale-95 shadow-2xl shadow-white/10"
            >
              Start Mimicking Now
            </button>
          </div>
        </section>
      </div>

      {showDemo && (
        <div className="fixed inset-0 bg-black/80 z-[100] flex items-center justify-center cursor-pointer"
          onClick={() => setShowDemo(false)}>
          <video src="samples/VideoProject.mp4" controls autoPlay className="max-w-3xl w-full rounded-2xl cursor-default" onClick={(e) => e.stopPropagation()} />
        </div>
      )}
    </div>
  );
}

export function UserGuide({ onNavigate, isLoggedIn }: ScreenProps) {
  return (
    <div className="pt-32 pb-24">
      <div className="max-w-[1440px] mx-auto px-6 md:px-12">
        <section className="flex flex-col lg:flex-row items-center gap-20 mb-32">
          <div className="w-full lg:w-3/5">
            <h1 className="text-5xl md:text-8xl font-black tracking-tighter leading-[0.9] text-on-surface uppercase mb-8">
              Mastering <br /> Motion Transfer
            </h1>
            <p className="text-lg text-on-surface-variant max-w-xl mb-12 leading-relaxed">
              Transform static identities into dynamic performers. Motion Mimic uses high-precision AI to map complex biomechanics from video source to image target with cinematic fidelity.
            </p>
            <div className="flex flex-wrap gap-4">
              <span className="inline-flex items-center gap-2 px-6 py-3 bg-surface-container-low rounded-full text-xs font-black tracking-widest uppercase">
                <Play className="w-4 h-4 fill-current" />
                Interactive Guide
              </span>
              <span className="inline-flex items-center gap-2 px-6 py-3 bg-surface-container-low rounded-full text-xs font-black tracking-widest uppercase">
                <Zap className="w-4 h-4 fill-current" />
                AI Engine v4.2
              </span>
            </div>
          </div>
          <div className="w-full lg:w-2/5 relative pb-6 pl-6">
            <div className="aspect-[4/5] bg-white rounded-3xl shadow-2xl overflow-hidden">
              <img
                src="https://picsum.photos/seed/guide-hero/800/1000"
                alt="Guide Hero"
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            </div>
            <div className="absolute -bottom-6 -left-6 p-6 bg-white shadow-2xl rounded-3xl hidden md:block">
              <div className="text-primary font-black text-4xl mb-1">99%</div>
              <div className="text-[10px] uppercase tracking-widest font-black text-on-surface-variant">Motion Accuracy</div>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-32">
          {[
            { id: "01", title: "Upload Image", desc: "Provide a high-resolution source image. This acts as the visual identity or 'Skin' that will receive the motion.", icon: <Layers className="w-6 h-6" /> },
            { id: "02", title: "Upload Video", desc: "Upload the motion source. Our AI extracts bone-structure and skeletal dynamics from this video clip.", icon: <Play className="w-6 h-6" /> },
            { id: "03", title: "Generate", desc: "Initiate the transfer. The engine will merge the identity and the motion, outputting a seamless high-end render.", icon: <Zap className="w-6 h-6" /> }
          ].map((step) => (
            <div key={step.id} className="bg-white p-10 rounded-3xl shadow-xl hover:scale-105 transition-all duration-500 group">
              <div className="flex justify-between items-start mb-8">
                <span className="text-6xl font-black text-primary/10">{step.id}</span>
                <div className="w-12 h-12 bg-primary/5 rounded-xl flex items-center justify-center text-primary">
                  {step.icon}
                </div>
              </div>
              <h3 className="text-2xl font-bold uppercase tracking-tight mb-4">{step.title}</h3>
              <p className="text-on-surface-variant text-sm leading-relaxed mb-8">{step.desc}</p>
              <div className="aspect-video bg-surface-container-low rounded-2xl overflow-hidden">
                <img
                  src={`https://picsum.photos/seed/step${step.id}/600/400`}
                  alt={step.title}
                  className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
                  referrerPolicy="no-referrer"
                />
              </div>
            </div>
          ))}
        </section>

        <section className="bg-white rounded-[3rem] p-12 md:p-24 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-12 overflow-hidden relative">
          <div className="relative z-10">
            <h2 className="text-4xl md:text-7xl font-black uppercase tracking-tighter mb-8">Ready to animate?</h2>
            <button
              onClick={() => onNavigate("generate")}
              className="mimic-gradient text-on-primary px-12 py-6 rounded-full font-bold text-xl shadow-xl shadow-primary/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-4"
            >
              Go to Generator
              <ArrowRight className="w-6 h-6" />
            </button>
          </div>
          <div className="w-full md:w-1/2 relative h-64 md:h-96">
            <img
              src="https://picsum.photos/seed/cta-guide/800/800"
              alt="CTA"
              className="w-full h-full object-cover rounded-2xl opacity-20"
              referrerPolicy="no-referrer"
            />
          </div>
        </section>
      </div>
    </div>
  );
}

export function GenerateWorkspace({ onNavigate, isLoggedIn }: ScreenProps) {
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  const [drivingVideo, setDrivingVideo] = useState<string | null>(null);
  const [sourceFile, setSourceFile] = useState<File | null>(null);
  const [drivingFile, setDrivingFile] = useState<File | null>(null);
  const [activeOption, setActiveOption] = useState<"motion" | "face">("motion");
  const [videoMode, setVideoMode] = useState<"sample" | "user">("user");
  const [selectedSample, setSelectedSample] = useState<number | null>(null);
  const sourceInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [jobStatus, setJobStatus] = useState<string>("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobMessage, setJobMessage] = useState<string>("");

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const pollStatus = (id: string) => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    intervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/status/${id}`);

        if (res.status === 401) {
          clearInterval(intervalRef.current!);
          onNavigate("auth");
          return;
        }

        const data = await res.json();
        setJobStatus(data.status);
        setJobMessage(data.message || data.status);

        if (data.ready || data.status === "error" || data.status === "done") {
          clearInterval(intervalRef.current!);
        }
      } catch (e) {
        // ignore
      }
    }, 2000);
  };

  const handleGenerate = async () => {
    if (!isLoggedIn) {
      onNavigate("auth");
      return;
    }

    if (!sourceFile) return alert("Please upload a source image.");
    if (videoMode === "user" && !drivingFile) return alert("Please upload a driving video.");
    if (videoMode === "sample" && !selectedSample) return alert("Please select a sample video.");

    setJobId(null);
    setJobStatus("queued");
    setJobMessage("Queued...");

    const formData = new FormData();
    formData.append("source_image", sourceFile);

    if (videoMode === "sample" && selectedSample) {
      formData.append("use_sample", selectedSample.toString());
    } else if (drivingFile) {
      formData.append("driving_video", drivingFile);
    }

    formData.append("mode", activeOption === "motion" ? "animate" : "face_composition");

    try {
      const res = await fetch("/generate", {
        method: "POST",
        body: formData,
      });

      if (res.status === 401) {
        onNavigate("auth");
        return;
      }

      const data = await res.json();
      if (data.error) {
        setJobStatus("error");
        setJobMessage(data.error);
        return;
      }
      setJobId(data.job_id);
      pollStatus(data.job_id);
    } catch (e: any) {
      setJobStatus("error");
      setJobMessage(e.message);
    }
  };

  const handleGenerateAnother = () => {
    setSourceImage(null);
    setSourceFile(null);
    setDrivingVideo(null);
    setDrivingFile(null);
    setSelectedSample(null);
    setJobId(null);
    setJobStatus("idle");
    setJobMessage("");
    if (sourceInputRef.current) sourceInputRef.current.value = "";
    if (videoInputRef.current) videoInputRef.current.value = "";
  };

  const handleSourceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSourceFile(file);
      setSourceImage(URL.createObjectURL(file));
    }
  };

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDrivingFile(file);
      setDrivingVideo(file.name);
    }
  };

  const handleUseExample = async (i: number) => {
    try {
      const response = await fetch(`/example_${i}.jpg`);
      const blob = await response.blob();
      const file = new File([blob], `example_${i}.jpg`, { type: blob.type || "image/jpeg" });
      setSourceFile(file);
      setSourceImage(URL.createObjectURL(file));
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      console.error(e);
      alert("Failed to load example image");
    }
  };

  const handleUseDrivingSample = (i: number) => {
    setVideoMode("sample");
    setSelectedSample(i);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="pt-32 pb-24">
      <div className="max-w-[1600px] mx-auto px-6 md:px-12">
        <header className="mb-12">
          <p className="text-on-surface-variant max-w-xl text-base">
            Orchestrate seamless motion between any static image and driving video. Precision-engineered AI for high-end editorial production.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Controls */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white p-6 rounded-3xl shadow-xl">
              <div className="flex justify-between items-center mb-4">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant">01. Source Identity</span>
                <Layers className="w-4 h-4 text-primary" />
              </div>
              <input
                type="file"
                ref={sourceInputRef}
                className="hidden"
                accept="image/*"
                onChange={handleSourceUpload}
              />
              <div
                onClick={() => sourceInputRef.current?.click()}
                className="h-40 bg-surface-container-low rounded-2xl border-2 border-dashed border-stone-300 flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-colors group overflow-hidden relative"
              >
                {sourceImage ? (
                  <img src={sourceImage} className="w-full h-full object-cover" alt="Source" referrerPolicy="no-referrer" />
                ) : (
                  <>
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg mb-3 group-hover:scale-110 transition-transform">
                      <ImageIcon className="w-6 h-6 text-primary" />
                    </div>
                    <p className="font-bold text-xs uppercase tracking-widest">Upload Source Image</p>
                  </>
                )}
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl shadow-xl">
              <div className="flex justify-between items-center mb-4">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant">02. Driving Video</span>
                <div className="flex bg-surface-container-low p-0.5 rounded-full">
                  <button
                    onClick={() => {
                      setVideoMode("sample");
                      setSelectedSample(null);
                      setDrivingFile(null);
                      setDrivingVideo(null);
                    }}
                    className={`px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest transition-all ${videoMode === "sample" ? "bg-white text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                      }`}
                  >
                    Sample
                  </button>
                  <button
                    onClick={() => {
                      setVideoMode("user");
                      setSelectedSample(null);
                      setDrivingFile(null);
                      setDrivingVideo(null);
                    }}
                    className={`px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest transition-all ${videoMode === "user" ? "bg-white text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                      }`}
                  >
                    User Input
                  </button>
                </div>
              </div>
              <input
                type="file"
                ref={videoInputRef}
                className="hidden"
                accept="video/*"
                onChange={handleVideoUpload}
              />
              <div
                onClick={() => videoMode === "user" && videoInputRef.current?.click()}
                className={`h-40 bg-surface-container-low rounded-2xl border-2 border-dashed border-stone-300 flex flex-col items-center justify-center transition-colors group overflow-hidden relative ${videoMode === "user" ? "cursor-pointer hover:border-primary" : "cursor-default"}`}
              >
                {videoMode === "sample" ? (
                  <div className="flex flex-col items-center gap-3">
                    <div className="flex gap-2">
                      {[1, 2, 3, 4].map(i => (
                        <div
                          key={i}
                          onClick={() => setSelectedSample(i)}
                          className={`w-16 h-16 bg-white rounded-lg overflow-hidden shadow-sm cursor-pointer border-2 transition-all relative ${selectedSample === i ? 'border-primary scale-105' : 'border-transparent hover:border-primary'
                            }`}
                        >
                          <video
                            src={`/sample-video/${i}`}
                            className="w-full h-full object-cover"
                            muted
                            playsInline
                            onLoadedData={(e) => {
                              e.currentTarget.currentTime = 0;
                            }}
                          />
                          {selectedSample === i && (
                            <div className="absolute inset-0 bg-primary/30 flex items-center justify-center">
                              <CheckCircle2 className="w-6 h-6 text-white fill-primary" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    <p className="text-[9px] font-black uppercase tracking-widest text-on-surface-variant">
                      {selectedSample ? `Sample ${selectedSample} Selected` : "Select a sample clip"}
                    </p>
                  </div>
                ) : drivingVideo ? (
                  <div className="flex flex-col items-center gap-2">
                    <CheckCircle2 className="w-8 h-8 text-primary" />
                    <p className="text-xs font-bold truncate max-w-[200px]">{drivingVideo}</p>
                  </div>
                ) : (
                  <>
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg mb-3 group-hover:scale-110 transition-transform">
                      <FileVideo className="w-6 h-6 text-primary" />
                    </div>
                    <p className="font-bold text-xs uppercase tracking-widest">Upload Driving Video</p>
                  </>
                )}
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={jobStatus === "processing" || jobStatus === "queued"}
              className={`w-full mimic-gradient text-on-primary py-5 rounded-full font-black text-base shadow-2xl shadow-primary/20 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-3 ${jobStatus === "processing" || jobStatus === "queued" ? "opacity-50 pointer-events-none" : ""
                }`}
            >
              <Zap className="w-5 h-5 fill-current" />
              {jobStatus === "processing" || jobStatus === "queued"
                ? jobMessage
                : isLoggedIn
                  ? "Generate Video"
                  : "Login to Generate"}
            </button>
          </div>

          {/* Viewport */}
          <div className="lg:col-span-8">
            <div className="bg-white rounded-[2rem] shadow-2xl overflow-hidden h-full flex flex-col min-h-[400px]">
              <div className="px-8 py-4 flex flex-col md:flex-row justify-between items-center border-b border-stone-100 gap-4">
                <div className="flex items-center gap-6">
                  <span className="text-[10px] font-black uppercase tracking-[0.2em]">Output Space</span>
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1.5 text-[9px] font-black text-primary uppercase tracking-widest">
                      <span className="w-1 h-1 rounded-full bg-primary" />
                      1080p
                    </span>
                  </div>
                </div>

                <div className="flex bg-surface-container-low p-1 rounded-full">
                  <button
                    onClick={() => setActiveOption("motion")}
                    className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${activeOption === "motion" ? "bg-white text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                      }`}
                  >
                    Motion Transfer
                  </button>
                  <button
                    onClick={() => setActiveOption("face")}
                    className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${activeOption === "face" ? "bg-white text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                      }`}
                  >
                    Face Composition
                  </button>
                </div>
              </div>

              <div className="flex-grow bg-surface-container-low flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
                {jobStatus === "done" && jobId ? (
                  <video src={`/download/${jobId}`} controls className="w-full h-full max-h-[400px] object-contain rounded-xl" autoPlay loop playsInline />
                ) : jobStatus === "processing" || jobStatus === "queued" ? (
                  <div className="flex flex-col items-center">
                    <Zap className="w-12 h-12 text-primary animate-pulse mb-6" />
                    <h3 className="text-2xl font-black uppercase tracking-tight mb-2">Processing</h3>
                    <p className="text-on-surface-variant text-sm max-w-xs mx-auto">{jobMessage}</p>
                  </div>
                ) : jobStatus === "error" ? (
                  <div className="flex flex-col items-center">
                    <div className="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center shadow-xl mb-6">
                      <Zap className="w-8 h-8 text-red-500" />
                    </div>
                    <h3 className="text-2xl font-black uppercase tracking-tight text-red-500 mb-2">Error Encountered</h3>
                    <p className="text-red-400 font-bold max-w-sm mx-auto">{jobMessage}</p>
                  </div>
                ) : (
                  <>
                    <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-xl mb-6">
                      <Layers className="w-8 h-8 text-stone-300" />
                    </div>
                    <h3 className="text-2xl font-black uppercase tracking-tight mb-2">Stage is Empty</h3>
                    <p className="text-on-surface-variant text-sm max-w-xs mx-auto">
                      Upload assets and click generate to initiate the neural motion transfer process.
                    </p>
                  </>
                )}
              </div>

              <div className="px-8 py-6 flex justify-between items-center bg-stone-50">
                <div className="flex gap-3">
                  {jobStatus === "done" && jobId && (
                    <button onClick={handleGenerateAnother} className="bg-white px-6 py-2 rounded-full font-bold text-xs shadow-md hover:scale-105 transition-transform inline-block">Generate Another</button>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-[9px] font-black uppercase tracking-widest text-stone-400">Status</p>
                  <p className={`font-black text-base ${jobStatus === "error" ? "text-red-500" : ""}`}>{jobStatus.toUpperCase()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Example Data Section */}
        <section className="mt-24">
          <div className="flex items-center gap-4 mb-12">
            <div className="h-[1px] flex-grow bg-stone-200" />
            <h2 className="text-2xl font-black uppercase tracking-tighter">Example Data</h2>
            <div className="h-[1px] flex-grow bg-stone-200" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="group cursor-pointer" onClick={() => handleUseExample(i)}>
                <div className="aspect-square bg-stone-100 rounded-2xl overflow-hidden mb-3 relative">
                  <img
                    src={`/example_${i}.jpg`}
                    alt={`Example ${i}`}
                    className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                    referrerPolicy="no-referrer"
                  />
                  <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <span className="text-white font-bold tracking-widest uppercase text-sm drop-shadow-md">Use This</span>
                  </div>
                </div>
                <p className="text-[10px] font-black uppercase tracking-widest text-center text-stone-500">Preset_0{i}</p>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 mb-12 mt-24">
            <div className="h-[1px] flex-grow bg-stone-200" />
            <h2 className="text-2xl font-black uppercase tracking-tighter">Driving Video Examples</h2>
            <div className="h-[1px] flex-grow bg-stone-200" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[1, 2, 3, 4].map((i) => (
              <div key={`driving-${i}`} className="flex flex-col gap-3">
                <div className="aspect-square bg-stone-100 rounded-2xl overflow-hidden relative shadow-sm">
                  <video
                    src={`/sample-video/${i}`}
                    className="w-full h-full object-cover"
                    playsInline
                    controls
                    preload="metadata"
                  />
                </div>
                <div className="flex justify-between items-center px-1">
                  <p className="text-[10px] font-black uppercase tracking-widest text-stone-500">Driving_0{i}</p>
                  <button onClick={() => handleUseDrivingSample(i)} className="text-[10px] bg-primary text-white px-4 py-1.5 rounded-full font-bold uppercase tracking-widest hover:scale-105 transition-transform shadow-md">Use This</button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export function Authentication({ onNavigate, onLogin }: ScreenProps) {
  const [view, setView] = useState<"login" | "forgot" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [resetSent, setResetSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    if (view === "forgot") {
      setResetSent(true);
      return;
    }

    try {
      const endpoint = view === "login" ? "/api/login" : "/api/register";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        if (onLogin) onLogin();
        onNavigate("landing");
      } else {
        setErrorMsg(data.error || "Authentication failed");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Network error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-24 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-[-10%] left-[-5%] w-[40%] h-[60%] bg-primary/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[60%] bg-primary/5 blur-[120px] rounded-full" />
      </div>

      <div className="max-w-5xl w-full grid grid-cols-1 lg:grid-cols-12 gap-20 items-center relative z-10">
        <div className="lg:col-span-7 space-y-12">
          <div className="space-y-6">
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9] uppercase">
              Precision <br />
              <span className="text-primary italic">Motion</span> Transfer.
            </h1>
            <p className="text-xl text-on-surface-variant max-w-md leading-relaxed font-medium">
              Seamlessly migrate architectural 3D motion data with enterprise-grade clinical precision.
            </p>
          </div>

          <div className="relative aspect-video rounded-3xl overflow-hidden shadow-2xl group">
            <img
              src="https://picsum.photos/seed/auth-visual/1200/800"
              alt="Auth Visual"
              className="w-full h-full object-cover grayscale opacity-80 group-hover:grayscale-0 transition-all duration-1000"
              referrerPolicy="no-referrer"
            />
            <div className="absolute bottom-8 left-8 flex items-center gap-3">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white">System Status: Optimal</span>
            </div>
          </div>
        </div>

        <div className="lg:col-span-5">
          <div className="bg-white p-10 md:p-16 rounded-[3rem] shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16 blur-3xl" />

            <div className="relative space-y-10">
              <div className="space-y-2">
                <h2 className="text-3xl font-black tracking-tight uppercase">
                  {view === "login" ? "Welcome Back" : view === "forgot" ? "Reset Access" : "Create Account"}
                </h2>
                <p className="text-on-surface-variant">
                  {view === "login"
                    ? "Enter your credentials to access your studio."
                    : view === "forgot"
                      ? "Enter your email to receive a reset link."
                      : "Join Motion Mimic to start generating precision motion."}
                </p>
              </div>

              {view === "login" && (
                <div className="grid grid-cols-1 gap-4">
                  <button
                    onClick={onLogin}
                    className="flex items-center justify-center gap-3 py-4 px-6 rounded-full bg-surface-container-low hover:bg-surface-container-high transition-all font-bold text-[10px] uppercase tracking-widest"
                  >
                    Continue with Google
                  </button>
                </div>
              )}

              {view === "login" && (
                <div className="relative flex items-center justify-center">
                  <div className="w-full h-[1px] bg-stone-100" />
                  <span className="absolute bg-white px-4 text-[10px] font-black uppercase tracking-[0.2em] text-stone-400">Or continue with</span>
                </div>
              )}

              <form className="space-y-8" onSubmit={handleSubmit}>
                {view === "forgot" && resetSent && (
                  <div className="p-4 bg-green-50 text-green-700 rounded-2xl text-sm font-bold text-center mb-4">
                    Reset link sent to {email}
                  </div>
                )}
                <div className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant">Email Address</label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-surface-container-low border-none focus:ring-2 focus:ring-primary rounded-2xl py-4 px-6 text-sm"
                      placeholder="name@kinetic.ai"
                    />
                  </div>
                  {view !== "forgot" && (
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <label className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant">Password</label>
                        {view === "login" && (
                          <button
                            type="button"
                            onClick={() => setView("forgot")}
                            className="text-[10px] font-black uppercase tracking-[0.2em] text-primary"
                          >
                            Forgot?
                          </button>
                        )}
                      </div>
                      <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full bg-surface-container-low border-none focus:ring-2 focus:ring-primary rounded-2xl py-4 px-6 text-sm"
                        placeholder="••••••••"
                      />
                    </div>
                  )}
                </div>

                {errorMsg && <p className="text-red-500 text-sm font-bold text-center">{errorMsg}</p>}
                <button
                  type="submit"
                  className="w-full mimic-gradient text-on-primary font-black py-5 rounded-full shadow-xl shadow-primary/20 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-3 group"
                >
                  <span className="uppercase tracking-widest text-xs">
                    {view === "login" ? "Initialize Session" : view === "forgot" ? "Send Reset Link" : "Create Account"}
                  </span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </form>

              <div className="text-center">
                {view === "login" ? (
                  <p className="text-sm text-on-surface-variant">
                    New to Motion Mimic? <button onClick={() => setView("signup")} className="text-primary font-bold hover:underline">Create an account</button>
                  </p>
                ) : (
                  <button onClick={() => setView("login")} className="text-sm text-primary font-bold hover:underline">Back to Login</button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function AboutPage({ onNavigate, isLoggedIn }: ScreenProps) {
  return (
    <div className="pt-32 pb-24">
      <div className="max-w-[1440px] mx-auto px-6 md:px-12">
        <section className="mb-24">
          <h1 className="text-5xl md:text-8xl font-black tracking-tighter leading-[0.9] text-on-surface uppercase mb-12">
            About <br />
            <span className="text-primary italic">Motion Transfer</span>
          </h1>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <p className="text-xl text-on-surface-variant leading-relaxed">
                Motion transfer is a cutting-edge AI technology that allows the movement from a source video to be applied to a target static image. This process involves complex neural networks that decouple appearance from motion.
              </p>
              <p className="text-lg text-on-surface-variant leading-relaxed">
                By extracting skeletal keypoints and optical flow from the driving video, our engine can re-synthesize the target image in a way that respects its original geometry while adopting new kinetic behaviors.
              </p>
              <div className="flex gap-4">
                <div className="bg-surface-container-low p-6 rounded-2xl flex-1">
                  <h4 className="font-bold uppercase tracking-tight mb-2">Neural Mapping</h4>
                  <p className="text-xs text-on-surface-variant">High-fidelity skeletal extraction and mapping.</p>
                </div>
                <div className="bg-surface-container-low p-6 rounded-2xl flex-1">
                  <h4 className="font-bold uppercase tracking-tight mb-2">Style Preservation</h4>
                  <p className="text-xs text-on-surface-variant">Maintains the unique identity of the source image.</p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-[3rem] overflow-hidden shadow-2xl">
                <img
                  src="https://picsum.photos/seed/motion-transfer-1/800/800"
                  alt="Motion Transfer Tech"
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="absolute -bottom-6 -right-6 bg-white p-8 rounded-3xl shadow-2xl hidden md:block">
                <p className="text-primary font-black text-4xl">MM.0</p>
                <p className="text-[10px] uppercase tracking-widest font-black text-on-surface-variant">Next-Gen Engine</p>
              </div>
            </div>
          </div>
        </section>

        <section className="mb-24">
          <h2 className="text-3xl md:text-5xl font-black uppercase tracking-tighter mb-12">The Process</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-6">
              <div className="aspect-video rounded-2xl overflow-hidden shadow-lg">
                <img src="https://picsum.photos/seed/process-1/600/400" alt="Analysis" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tight">01. Analysis</h3>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                The AI analyzes the driving video to identify key joints and movement patterns, creating a digital skeleton.
              </p>
            </div>
            <div className="space-y-6">
              <div className="aspect-video rounded-2xl overflow-hidden shadow-lg">
                <img src="https://picsum.photos/seed/process-2/600/400" alt="Synthesis" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tight">02. Synthesis</h3>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                The target image is projected into a latent space where it can be manipulated without losing its core features.
              </p>
            </div>
            <div className="space-y-6">
              <div className="aspect-video rounded-2xl overflow-hidden shadow-lg">
                <img src="https://picsum.photos/seed/process-3/600/400" alt="Rendering" className="w-full h-full object-cover" referrerPolicy="no-referrer" />
              </div>
              <h3 className="text-xl font-bold uppercase tracking-tight">03. Rendering</h3>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                The final frames are rendered with temporal consistency, ensuring smooth and realistic motion.
              </p>
            </div>
          </div>
        </section>

        <section className="bg-stone-950 rounded-[3rem] p-12 md:p-24 text-center relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-4xl md:text-6xl font-black text-white uppercase tracking-tighter mb-8">
              Experience the future of animation.
            </h2>
            <button
              onClick={() => onNavigate("generate")}
              className="bg-white text-stone-950 px-12 py-6 rounded-full font-bold text-xl hover:bg-stone-200 transition-all active:scale-95"
            >
              Get Started
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
