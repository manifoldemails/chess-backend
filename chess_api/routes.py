from fastapi import APIRouter, HTTPException
import chess
import chess.engine
import os
from stockfish import Stockfish
from chess_api.schemas import MoveData, MoveRequest, MoveResponse

router = APIRouter(prefix="/chess", tags=["Chess"])

#STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/opt/homebrew/bin/stockfish")  # default Linux path
# adjust for your OS
# Assume this script is at /path/to/your/project/some_folder/your_script.py
SCRIPT_DIR = os.path.dirname(__file__)
# This line correctly moves up one directory
STOCKFISH_MAC_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../bin/stockfish_mac/stockfish-macos-m1-apple-silicon"))
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", STOCKFISH_MAC_PATH)
#STOCKFISH_UBUNTU_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../bin/stockfish_ubuntu/stockfish-ubuntu-x86-64-avx2")) # The Linux binary name

@router.post("/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    try:
        # Handle the start position safely
        if request.fen.strip().lower() in ["start", "", None]:
            board = chess.Board()  # start position
        else:
            board = chess.Board(request.fen)

        # Construct the move
        uci_move_str = request.move.from_ + request.move.to
        uci_move = chess.Move.from_uci(uci_move_str)

        # Check move legality
        if uci_move not in board.legal_moves:
            raise HTTPException(
                status_code=400,
                detail=f"Illegal move: {uci_move_str}, Legal moves: {[m.uci() for m in board.legal_moves]}"
            )

        # Apply player move
        board.push(uci_move)

        # Check for game over
        if board.is_game_over():
            return MoveResponse(fen=board.fen(), bot_move="")

        # Run Stockfish to get bot move
        # Initialize Python Stockfish
        stockfish = Stockfish(path=STOCKFISH_PATH,parameters={"Threads": 2, "Minimum Thinking Time": 30})
        stockfish.set_fen_position(board.fen())
        best_move = stockfish.get_best_move()

        board.push(chess.Move.from_uci(best_move))

        return MoveResponse(fen=board.fen(), bot_move=best_move)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {request.fen}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Stockfish not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
