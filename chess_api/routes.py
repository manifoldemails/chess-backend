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
STOCKFISH_MAC_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "./bin/stockfish_mac/stockfish-macos-m1-apple-silicon"))
#STOCKFISH_UBUNTU_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../bin/stockfish_ubuntu/stockfish-ubuntu-x86-64-avx2")) # The Linux binary name
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", STOCKFISH_MAC_PATH)

@router.post("/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    try:
        result = None
        # Handle the start position safely
        if request.fen.strip().lower() in ["start", "", None]:
            board = chess.Board()  # start position
        else:
            board = chess.Board(request.fen)

        # Construct the move
        uci_move_str = request.move.from_ + request.move.to
        uci_move = chess.Move.from_uci(uci_move_str)

        #not needed for nowif board.turn != (request.move.color == "w"):
        #    raise HTTPException(status_code=400, detail=f"It's not {request.move.color}'s turn.")

        # Check move legality
        if uci_move not in board.legal_moves:
            raise HTTPException(
                status_code=400,
                detail=f"Illegal move: {uci_move_str}, Legal moves: {[m.uci() for m in board.legal_moves]}"
            )

        # Apply player move
        board.push(uci_move)

        # Check if the player's move ended the game
        if board.is_checkmate():
            return MoveResponse(fen=board.fen(), bot_move="", result="Checkmate! You win 🎉")
        elif board.is_stalemate():
            return MoveResponse(fen=board.fen(), bot_move="", result="Stalemate 🤝")
        elif board.is_insufficient_material():
            return MoveResponse(fen=board.fen(), bot_move="", result="Draw (insufficient material)")
        elif board.is_seventyfive_moves():
            return MoveResponse(fen=board.fen(), bot_move="", result="Draw (75-move rule)")
        elif board.is_fivefold_repetition():
            return MoveResponse(fen=board.fen(), bot_move="", result="Draw (fivefold repetition)")

        #  Bot makes its move only if game not over
        stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2, "Minimum Thinking Time": 30,"Skill Level": request.difficulty})
        stockfish.set_fen_position(board.fen())
        best_move = stockfish.get_best_move()

        if not best_move:
            return MoveResponse(fen=board.fen(), bot_move="", result="Game over - no legal moves for bot")

        bot_move = chess.Move.from_uci(best_move)
        board.push(bot_move)

        # Recheck if the bot caused checkmate
        if board.is_checkmate():
            result = "Checkmate! Bot wins 🤖"
        elif board.is_stalemate():
            result = "Stalemate 🤝"
        elif board.is_insufficient_material():
            result = "Draw (insufficient material)"
        elif board.is_seventyfive_moves():
            result = "Draw (75-move rule)"
        elif board.is_fivefold_repetition():
            result = "Draw (fivefold repetition)"
        else:
            result = None

        return MoveResponse(fen=board.fen(), bot_move=best_move, result=result)


    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {request.fen}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Stockfish not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
