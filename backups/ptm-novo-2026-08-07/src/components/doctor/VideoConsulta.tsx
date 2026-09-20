"use client";

interface Props {
  roomUrl: string;
  onEnd: () => void;
}

export default function VideoConsulta({ roomUrl, onEnd }: Props) {
  return (
    <div className="relative w-full h-[500px] bg-gray-900 rounded-xl overflow-hidden">
      <iframe
        src={roomUrl}
        allow="camera; microphone; fullscreen; speaker; display-capture"
        className="w-full h-full border-0 rounded-xl"
      />
      <button
        onClick={onEnd}
        className="absolute bottom-4 right-4 px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition-colors"
      >
        Terminar orientación
      </button>
    </div>
  );
}
