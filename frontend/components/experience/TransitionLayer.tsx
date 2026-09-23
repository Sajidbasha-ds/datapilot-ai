"use client";

import { useEffect, useRef, useState } from "react";

interface TransitionLayerProps {
  children: React.ReactNode;
  className?: string;
}

export function TransitionLayer({ children, className = "" }: TransitionLayerProps) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const section = sectionRef.current;
    if (!section || typeof IntersectionObserver === "undefined") {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.08 },
    );
    observer.observe(section);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={sectionRef} className={`experience-reveal ${isVisible ? "experience-reveal-visible" : ""} ${className}`}>
      {children}
    </div>
  );
}
