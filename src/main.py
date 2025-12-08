import os
import json
import enum
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel

# =============================================================================
# 1. DATABASE SETUP
# =============================================================================
# Tenta ler do Render/Neon, senão usa ficheiro local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./football.db")

# Correção necessária para o Render/Neon (postgres -> postgresql)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =============================================================================
# 2. DATABASE MODELS
# =============================================================================

class MatchResult(str, enum.Enum):
    TEAM_A = "TEAM_A"
    TEAM_B = "TEAM_B"
    DRAW = "DRAW"

class MatchPlayer(Base):
    __tablename__ = "match_players"
    match_id = Column(Integer, ForeignKey("matches.id"), primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    team = Column(String, nullable=False)

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    balance = Column(Float, default=0.0)
    matches = relationship("Match", secondary="match_players", back_populates="players")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    result = Column(String, nullable=False)
    is_double_points = Column(Boolean, default=False)
    players = relationship("Player", secondary="match_players", back_populates="matches")

class Champion(Base):
    __tablename__ = "champions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    titles = Column(Integer, default=1)

class SeasonArchive(Base):
    __tablename__ = "season_archive"
    id = Column(Integer, primary_key=True, index=True)
    season_name = Column(String)
    data_json = Column(Text)
    date = Column(Date)

# Cria as tabelas na Base de Dados
Base.metadata.create_all(bind=engine)

# =============================================================================
# 3. PYDANTIC SCHEMAS
# =============================================================================

class PlayerCreate(BaseModel):
    name: str

class PaymentSchema(BaseModel):
    player_id: int
    amount: float

class PlayerSchema(BaseModel):
    id: int
    name: str
    balance: float
    is_active: bool
    class Config: from_attributes = True

class MatchCreate(BaseModel):
    date: date
    result: MatchResult
    team_a_players: List[int]
    team_b_players: List[int]
    goalkeepers: List[int] = [] # IDs dos GRs que não pagam
    is_double_points: bool = False

class ChampionSchema(BaseModel):
    name: str
    titles: int
    class Config: from_attributes = True

class CloseSeasonSchema(BaseModel):
    champion_name: str
    season_name: str

class ArchiveSchema(BaseModel):
    id: int
    season_name: str
    date: date
    data_json: str
    class Config: from_attributes = True

# =============================================================================
# 4. API LOGIC
# =============================================================================

app = FastAPI(title="Terças FC API V3.3")

# AQUI ESTAVA O ERRO DE INDENTAÇÃO. AGORA ESTÁ CORRIGIDO:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Lógica de Cálculo da Tabela ---
def calculate_table_stats(db: Session):
    players = db.query(Player).filter(Player.is_active == True).all()
    matches = db.query(Match).all()
    stats = {p.id: {"id": p.id, "name": p.name, "games_played": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0} for p in players}

    for m in matches:
        multiplier = 2 if m.is_double_points else 1
        links = db.query(MatchPlayer).filter(MatchPlayer.match_id == m.id).all()
        for link in links:
            pid = link.player_id
            if pid not in stats: continue
            stats[pid]["games_played"] += 1
            if m.result == "DRAW":
                stats[pid]["draws"] += 1; stats[pid]["points"] += (2 * multiplier)
            elif (m.result == "TEAM_A" and link.team == "A") or (m.result == "TEAM_B" and link.team == "B"):
                stats[pid]["wins"] += 1; stats[pid]["points"] += (3 * multiplier)
            else:
                stats[pid]["losses"] += 1; stats[pid]["points"] += (1 * multiplier)

    res = list(stats.values())
    res.sort(key=lambda x: (x["points"], x["games_played"]), reverse=True)
    return res

# --- ENDPOINTS ---

@app.get("/table/")
def get_table(db: Session = Depends(get_db)):
    return calculate_table_stats(db)

@app.post("/players/", response_model=PlayerSchema)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    if db.query(Player).filter(Player.name == player.name).first(): raise HTTPException(400, "Exists")
    new_player = Player(name=player.name, balance=0.0, is_active=True)
    db.add(new_player); db.commit(); db.refresh(new_player)
    return new_player

@app.get("/players/", response_model=List[PlayerSchema])
def read_players(db: Session = Depends(get_db)):
    return db.query(Player).filter(Player.is_active == True).all()

@app.get("/players/all", response_model=List[PlayerSchema])
def read_all_players(db: Session = Depends(get_db)):
    return db.query(Player).all()

@app.post("/players/pay")
def register_payment(payment: PaymentSchema, db: Session = Depends(get_db)):
    p = db.query(Player).filter(Player.id == payment.player_id).first()
    if not p: raise HTTPException(404, "Not found")
    p.balance += payment.amount; db.commit()
    return {"message": "Paid"}

@app.post("/matches/")
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    db_match = Match(date=match.date, result=match.result, is_double_points=match.is_double_points)
    db.add(db_match); db.commit(); db.refresh(db_match)

    GAME_COST = 3.0
    all_pids = match.team_a_players + match.team_b_players

    for pid in all_pids:
        team = "A" if pid in match.team_a_players else "B"
        db.add(MatchPlayer(match_id=db_match.id, player_id=pid, team=team))

        # REGRA DOS GUARDA-REDES:
        # Se o ID do jogador NÃO estiver na lista de GRs, cobra 3€.
        # Se estiver, não faz nada (não paga).
        if pid not in match.goalkeepers:
            p = db.query(Player).filter(Player.id == pid).first()
            if p: p.balance -= GAME_COST

    db.commit()
    return {"message": "Match created"}

# -- CAMPEÕES & HISTÓRICO --

@app.get("/champions/", response_model=List[ChampionSchema])
def get_champions(db: Session = Depends(get_db)):
    return db.query(Champion).order_by(Champion.titles.desc()).all()

@app.post("/champions/remove")
def remove_champion(data: PlayerCreate, db: Session = Depends(get_db)):
    champ = db.query(Champion).filter(Champion.name == data.name).first()
    if not champ: raise HTTPException(404, "Not found")
    if champ.titles > 1: champ.titles -= 1
    else: db.delete(champ)
    db.commit()
    return {"message": "Title removed"}

@app.post("/season/close")
def close_season(data: CloseSeasonSchema, db: Session = Depends(get_db)):
    # 1. Atualizar Campeão
    champ = db.query(Champion).filter(Champion.name == data.champion_name).first()
    if champ: champ.titles += 1
    else: db.add(Champion(name=data.champion_name, titles=1))

    # 2. Guardar Histórico (Snapshot JSON)
    final_stats = calculate_table_stats(db)
    archive = SeasonArchive(season_name=f"{data.season_name} ({date.today()})", date=date.today(), data_json=json.dumps(final_stats))
    db.add(archive)

    # 3. Limpar Jogos
    db.query(MatchPlayer).delete(); db.query(Match).delete()
    db.commit()
    return {"message": "Season closed!"}

@app.get("/history/", response_model=List[ArchiveSchema])
def get_history(db: Session = Depends(get_db)):
    return db.query(SeasonArchive).order_by(SeasonArchive.date.desc()).all()

@app.delete("/history/{archive_id}")
def delete_history_entry(archive_id: int, db: Session = Depends(get_db)):
    archive = db.query(SeasonArchive).filter(SeasonArchive.id == archive_id).first()
    if not archive: raise HTTPException(404, "Not found")
    db.delete(archive)
    db.commit()
    return {"message": "Deleted"}

@app.delete("/reset/")
def reset_manual(db: Session = Depends(get_db)):
    db.query(MatchPlayer).delete(); db.query(Match).delete(); db.commit()
    return {"message": "Reset done"}