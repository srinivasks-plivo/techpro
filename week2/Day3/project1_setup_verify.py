"""
Project 1: Install Pipecat and Verify Setup
============================================
This script verifies that Pipecat is installed correctly with all required
dependencies and that environment variables are configured.

Pipecat Architecture:
    Audio In -> VAD -> STT -> LLM -> TTS -> Audio Out

Key Concepts:
    - Frames: Units of data flowing through pipeline (audio, text, control)
    - Processors: Transform frames (STT processor, LLM processor, etc.)
    - Pipeline: Chain of processors
    - Transport: How audio gets in/out (Daily, local audio, WebSocket)
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


def check_import(module_path, description):
    """Try importing a module and report success/failure."""
    try:
        parts = module_path.rsplit(".", 1)
        if len(parts) == 2:
            mod = __import__(parts[0], fromlist=[parts[1]])
            getattr(mod, parts[1])
        else:
            __import__(module_path)
        print(f"  [OK] {description}")
        return True
    except Exception as e:
        print(f"  [FAIL] {description}: {e}")
        return False


def main():
    print("=" * 60)
    print("Pipecat Setup Verification")
    print("=" * 60)

    # Check pipecat core
    print("\n1. Core Pipecat Framework:")
    results = []
    results.append(check_import("pipecat", "pipecat core"))
    results.append(check_import("pipecat.pipeline.pipeline.Pipeline", "Pipeline"))
    results.append(check_import("pipecat.pipeline.runner.PipelineRunner", "PipelineRunner"))
    results.append(check_import("pipecat.pipeline.task.PipelineTask", "PipelineTask"))
    results.append(check_import("pipecat.frames.frames.TTSSpeakFrame", "Frames"))

    # Check transport
    print("\n2. Local Audio Transport:")
    results.append(
        check_import(
            "pipecat.transports.local.audio.LocalAudioTransport",
            "LocalAudioTransport",
        )
    )

    # Check VAD
    print("\n3. Voice Activity Detection (SileroVAD):")
    results.append(
        check_import(
            "pipecat.audio.vad.silero.SileroVADAnalyzer",
            "SileroVADAnalyzer",
        )
    )

    # Check STT
    print("\n4. Speech-to-Text (Deepgram):")
    results.append(
        check_import(
            "pipecat.services.deepgram.stt.DeepgramSTTService",
            "DeepgramSTTService",
        )
    )

    # Check LLM
    print("\n5. LLM (OpenAI):")
    results.append(
        check_import(
            "pipecat.services.openai.llm.OpenAILLMService",
            "OpenAILLMService",
        )
    )

    # Check TTS
    print("\n6. Text-to-Speech (ElevenLabs):")
    results.append(
        check_import(
            "pipecat.services.elevenlabs.tts.ElevenLabsTTSService",
            "ElevenLabsTTSService",
        )
    )

    # Check SmartTurn
    print("\n7. SmartTurn (Turn Detection):")
    results.append(
        check_import(
            "pipecat.audio.turn.smart_turn.local_smart_turn_v3.LocalSmartTurnAnalyzerV3",
            "LocalSmartTurnAnalyzerV3",
        )
    )

    # Check context aggregators
    print("\n8. Context Aggregators:")
    results.append(
        check_import(
            "pipecat.processors.aggregators.llm_response_universal.LLMContextAggregatorPair",
            "LLMContextAggregatorPair",
        )
    )
    results.append(
        check_import(
            "pipecat.processors.aggregators.llm_context.LLMContext",
            "LLMContext",
        )
    )

    # Check function calling support
    print("\n9. Function Calling Support:")
    results.append(
        check_import(
            "pipecat.adapters.schemas.function_schema.FunctionSchema",
            "FunctionSchema",
        )
    )
    results.append(
        check_import(
            "pipecat.adapters.schemas.tools_schema.ToolsSchema",
            "ToolsSchema",
        )
    )

    # Check environment variables
    print("\n10. Environment Variables:")
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DEEPGRAM_API_KEY": os.getenv("DEEPGRAM_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
        "ELEVENLABS_VOICE_ID": os.getenv("ELEVENLABS_VOICE_ID"),
    }
    for var_name, var_value in env_vars.items():
        if var_value and not var_value.startswith("your_"):
            print(f"  [OK] {var_name} is set")
            results.append(True)
        else:
            print(f"  [WARN] {var_name} is not configured (set in .env)")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    if passed == total:
        print("All checks passed! Pipecat is ready to use.")
    else:
        print("Some checks failed. Review the output above.")
    print("=" * 60)

    # Print Pipecat version
    import pipecat

    print(f"\nPipecat version: {pipecat.__version__}")
    print(f"Python version: {sys.version}")


if __name__ == "__main__":
    main()
