import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MicrophoneIcon, VolumeUpIcon, StopIcon } from '@heroicons/react/outline';
import { toast } from 'react-hot-toast';

interface VoiceInterfaceProps {
  onTranscript: (transcript: string) => void;
  onSubmit: () => void;
  isProcessing: boolean;
}

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onTranscript,
  onSubmit,
  isProcessing,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState<any>(null);
  const [speechSynthesis, setSpeechSynthesis] = useState<SpeechSynthesis | null>(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onstart = () => {
        setIsListening(true);
        toast.success('Voice recognition started');
      };
      
      recognitionInstance.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        const fullTranscript = finalTranscript + interimTranscript;
        setTranscript(fullTranscript);
        onTranscript(fullTranscript);
      };
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        toast.error(`Voice recognition error: ${event.error}`);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
        toast.success('Voice recognition ended');
      };
      
      setRecognition(recognitionInstance);
    } else {
      toast.error('Speech recognition not supported in this browser');
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      setSpeechSynthesis(window.speechSynthesis);
    }
  }, [onTranscript]);

  const startListening = () => {
    if (recognition && !isListening && !isProcessing) {
      try {
        recognition.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        toast.error('Failed to start voice recognition');
      }
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  const speakText = (text: string) => {
    if (speechSynthesis && text.trim()) {
      // Stop any ongoing speech
      speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onstart = () => {
        setIsSpeaking(true);
        toast.success('Speaking...');
      };
      
      utterance.onend = () => {
        setIsSpeaking(false);
        toast.success('Finished speaking');
      };
      
      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        setIsSpeaking(false);
        toast.error('Speech synthesis error');
      };
      
      speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (speechSynthesis) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const handleVoiceSubmit = () => {
    if (transcript.trim()) {
      onSubmit();
      setTranscript('');
    }
  };

  return (
    <div className="flex flex-col space-y-2">
      {/* Voice Recognition Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={isListening ? stopListening : startListening}
        disabled={isProcessing}
        className={`p-2 rounded-lg transition-colors ${
          isListening
            ? 'bg-red-500 text-white animate-pulse'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
        title={isListening ? 'Stop listening' : 'Start voice input'}
      >
        {isListening ? (
          <StopIcon className="h-4 w-4" />
        ) : (
          <MicrophoneIcon className="h-4 w-4" />
        )}
      </motion.button>

      {/* Text-to-Speech Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => speakText(transcript)}
        disabled={!transcript.trim() || isSpeaking || isProcessing}
        className={`p-2 rounded-lg transition-colors ${
          isSpeaking
            ? 'bg-blue-500 text-white animate-pulse'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
        title="Speak the transcript"
      >
        {isSpeaking ? (
          <StopIcon className="h-4 w-4" />
        ) : (
          <VolumeUpIcon className="h-4 w-4" />
        )}
      </motion.button>

      {/* Voice Submit Button */}
      {transcript.trim() && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleVoiceSubmit}
          disabled={isProcessing}
          className="p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Submit voice input"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </motion.button>
      )}

      {/* Voice Status Indicator */}
      {(isListening || isSpeaking) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute -top-2 -right-2 w-3 h-3 bg-red-500 rounded-full animate-pulse"
        />
      )}

      {/* Voice Controls */}
      {isSpeaking && (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          onClick={stopSpeaking}
          className="mt-2 px-3 py-1 bg-red-500 text-white text-xs rounded-full hover:bg-red-600 transition-colors"
        >
          Stop Speaking
        </motion.button>
      )}

      {/* Transcript Display */}
      {transcript && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <p className="text-xs text-blue-800 font-medium mb-1">Voice Input:</p>
          <p className="text-sm text-blue-900">{transcript}</p>
        </motion.div>
      )}
    </div>
  );
};

export default VoiceInterface; 