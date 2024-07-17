from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from user_jwt import createToken, validateToken
from fastapi.security import HTTPBearer
from bd.database import Session, engine, Base
from models.movie import Movie as ModelMovie
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter

routerMovie = APIRouter()

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field( default='Titulo de la pelicula', min_length=5, max_length=60)
    overview: str = Field( default='Descripcion de la pelicula', min_length=15, max_length=60)
    year: int = Field( default=2024)
    rating: float = Field( ge=1, le=10)
    category: str = Field( min_length=3, max_length=15, default='Aqui va la categoria') 

class bearerJWT(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validateToken(auth.credentials)
        if data['email'] != 'juancamilo@gmail.com':
            raise HTTPException(status_code=403, detail='Credenciales incorrectas')

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field( default='Titulo de la pelicula', min_length=5, max_length=60)
    overview: str = Field( default='Descripcion de la pelicula', min_length=15, max_length=60)
    year: int = Field( default=2024)
    rating: float = Field( ge=1, le=10)
    category: str = Field( min_length=3, max_length=15, default='Aqui va la categoria')


@routerMovie.get('/movies', tags=['movies'], dependencies=[Depends(bearerJWT())])
def get_movies():
    db = Session()
    data = db.query(ModelMovie).all()
    return JSONResponse(content=jsonable_encoder(data))

@routerMovie.get('/movies/{id}', tags=['movies'], status_code=200)
def get_movie(id: int = Path(ge=1, le=100)):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={'message': 'Recurso no encontrado'})
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    
@routerMovie.get('/movies/', tags=['movies'])
def get_movies_by_category(category: str = Query(min_length=3, max_length=15)):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.category == category).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(data))

@routerMovie.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie):
    db = Session()
    newMovie = ModelMovie(**movie.dict())
    db.add(newMovie)
    db.commit()
    return JSONResponse(content={'message': 'Se ha cargado una nueva pelicula', 'movie': [movie.dict() for m in movies]})

@routerMovie.put('/movies/{id}', tags=['movies'], status_code=200)
def update_movie(id: int, movie:Movie):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={'message': 'No se encontro el recurso'})
    data.title = movie.title
    data.overview = movie.overview
    data.year = movie.year
    data.rating = movie.rating
    data.category = movie.category
    db.commit()
    return JSONResponse(content={'message':'Se ha modificado la pelicula'})
        
@routerMovie.delete('/movies/{id}', tags=['movies'], status_code=200)
def delete_movie(id:int):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
            return JSONResponse(status_code=404, content={'message': 'No se encontro el recurso'})
    db.delete(data)
    db.commit()
    return JSONResponse(content={'message':'Se ha eliminado la pelicula', 'data': jsonable_encoder(data)})