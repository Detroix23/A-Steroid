"""
# A-Steroid
main.py
"""

from typing import Final

import pyxel

TRANSPARENCY: Final[int] = 8
""" Clé de couleur pour la transparence. """


class Vector2D:
	"""
	# `Vector2D` 2 `float`s (x; y)
	"""
	x: float
	y: float

	def __init__(self, x: float, y: float) -> None:
		self.x = x
		self.y = y

	def __str__(self) -> str:
		return f"({self.x}; {self.y})"

	def __add__(self, other: object) -> 'Vector2D':
		if isinstance(other, Vector2D):
			return Vector2D(
				self.x + other.x,
				self.y + other.y,
			)
		else:
			return NotImplemented
	
	def __sub__(self, other: object) -> 'Vector2D':
		if isinstance(other, Vector2D):
			return Vector2D(
				self.x - other.x,
				self.y - other.y,
			)
		else:
			return NotImplemented

	def __mul__(self, other: object) -> 'Vector2D':
		if isinstance(other, float) or isinstance(other, int):
			return Vector2D(
				self.x * other,
				self.y * other,
			)
		else:
			return NotImplemented

	def __truediv__(self, other: object) -> 'Vector2D':
		if isinstance(other, float) or isinstance(other, int):
			return Vector2D(
				self.x / other,
				self.y / other,
			)
		else:
			return NotImplemented


class Player:
	"""
	# `Player` principal: le vaisseau.
	"""
	SPRITE_SHIP_IMAGE: int = 0
	SPRITE_SHIP_POSITION: tuple[int, int] = (0, 0)
	SPRITE_SHIP_SIZE: tuple[int, int] = (16, 16)

	parent_app: 'App'
	position: Vector2D
	inertia: Vector2D
	acceleration: float
	rotation: float
	drag: float

	def __init__(
		self, 
		parent_app: 'App',
		start_position: Vector2D,
		acceleration: float,
		drag: float,
	) -> None:
		"""
		Crée le `Player`, en renseignant son parent.
		"""
		self.parent_app = parent_app
		self.position = start_position
		self.inertia = Vector2D(0.0, 0.0)
		self.acceleration = acceleration
		self.drag = drag
		self.rotation = 0.0

	def forward_vector(self) -> Vector2D:
		"""
		Renvoie le `Vector2D` pointant tout-droit.
		"""
		return Vector2D(
			pyxel.cos(self.rotation - 90.0),
			pyxel.sin(self.rotation - 90.0),
		)

	def update(self) -> None:
		"""
		Gère le déplacement et les actions du joueur.
		"""
		# Direction.
		self.rotation = -pyxel.atan2(
			self.position.x - pyxel.mouse_x, 
			self.position.y - pyxel.mouse_y,
		)

		# Souris.
		if pyxel.btn(pyxel.KEY_UP):
			self.inertia += self.forward_vector() * self.acceleration
		if pyxel.btn(pyxel.KEY_DOWN):
			self.inertia += self.forward_vector() * (self.acceleration / -3.0)
		if pyxel.btn(pyxel.KEY_LEFT):
			inertia: Vector2D = Vector2D(
				pyxel.cos(self.rotation),
				pyxel.sin(self.rotation),
			)
			centripete: Vector2D = self.forward_vector()
			lateral: Vector2D = (centripete + inertia) * (self.acceleration / 2.0)
		
			self.inertia += lateral
		if pyxel.btn(pyxel.KEY_RIGHT):
			inertia: Vector2D = Vector2D(
				pyxel.cos(self.rotation),
				pyxel.sin(self.rotation),
			)
			centripete: Vector2D = self.forward_vector()
			lateral: Vector2D = (centripete - inertia) * (self.acceleration / 2.0)

			self.inertia += lateral

		# Position.
		self.position.x = pyxel.clamp(self.position.x + self.inertia.x, 0.0, pyxel.width)
		self.position.y = pyxel.clamp(self.position.y + self.inertia.y, 0.0, pyxel.height)
		self.inertia /= self.drag
		
		# Collisions.
		if self.position.x <= 0.0 or self.position.x >= pyxel.width:
			self.inertia.x *= (-1)
		if self.position.y <= 0.0 or self.position.y >= pyxel.height:
			self.inertia.y *= (-1)

	def draw(self) -> None:
		"""
		Dessine le vaisseau du joueur.
		"""
		pyxel.blt(
			self.position.x - Player.SPRITE_SHIP_SIZE[0] / 2,
			self.position.y - Player.SPRITE_SHIP_SIZE[1] / 2,
			Player.SPRITE_SHIP_IMAGE,
			Player.SPRITE_SHIP_POSITION[0],
			Player.SPRITE_SHIP_POSITION[1],
			Player.SPRITE_SHIP_SIZE[0],
			Player.SPRITE_SHIP_SIZE[1],
			colkey=TRANSPARENCY,
			rotate=self.rotation,
			scale=1.0
		)


class Ui:
	"""
	# Interface `Ui` du jeu.
	"""
	SPRITE_MOUSE_IMAGE: int = 0
	SPRITE_MOUSE_POSITION: tuple[int, int] = (0, 16)
	SPRITE_MOUSE_SIZE: tuple[int, int] = (16, 16)

	parent_app: 'App'
	camera_position: Vector2D
	space: pyxel.Tilemap

	def __init__(self, parent_app: 'App') -> None:
		"""
		Instancie la sous-class `Ui`.
		"""
		self.parent_app = parent_app
		self.camera_position = Vector2D(0.0, 0.0)

	def update(self) -> None:
		"""
		Mets à jour la camera.
		"""
		self.camera_position += self.parent_app.player.inertia
		self.camera_position /= 1.9	
		pyxel.camera(self.camera_position.x, self.camera_position.y)


	def draw(self) -> None:
		"""
		Dessine toute l'interface: souris, textes.
		"""
		# Souris animée.
		mouse_frame: int = abs(pyxel.floor(pyxel.frame_count / 4) % 7 - 3)
		pyxel.blt(
			pyxel.mouse_x - Ui.SPRITE_MOUSE_SIZE[0] // 2,
			pyxel.mouse_y - Ui.SPRITE_MOUSE_SIZE[1] // 2,
			Ui.SPRITE_MOUSE_IMAGE,
			Ui.SPRITE_MOUSE_POSITION[0] + mouse_frame * 16,
			Ui.SPRITE_MOUSE_POSITION[1],
			Ui.SPRITE_MOUSE_SIZE[0],
			Ui.SPRITE_MOUSE_SIZE[1],
			colkey=TRANSPARENCY,
		)


class App:
	"""
	# A-Steroid cadre principal d'execution `App`. 
	Englobe l'entiereté du jeu. 
	"""
	
	score: int
	ui: Ui
	player: Player

	def __init__(self) -> None:
		"""
		Crée l'`App`, le context `pyxel`, et lance la boucle.
		"""
		pyxel.init(
			width=256,
			height=256,
			title="A-Steroid",
			fps=30,
			quit_key=pyxel.KEY_ESCAPE,
		)

		self.score = 0
		self.ui = Ui(parent_app=self)
		self.player = Player(
			parent_app=self,
			start_position=Vector2D(pyxel.width / 2, pyxel.height / 2),
			acceleration=1.2,
			drag=1.1,
		)

		pyxel.camera()
		pyxel.load("theme.pyxres")

		print("(?) App() Lancage du jeu...")
		pyxel.run(self.update, self.draw)

	def update(self) -> None:
		"""
		Gère l'état du jeu, écoute les entrés.
		"""	
		self.ui.update()
		self.player.update()

	def draw(self) -> None:
		"""
		Dessine, affiche avec `pyxel` le jeu.
		"""
		pyxel.cls(0)

		# Décors
		pyxel.bltm(
			x=-16.0 + pyxel.ceil(self.ui.camera_position.x * 0.6),
			y=-16.0 + pyxel.ceil(self.ui.camera_position.y * 0.6),
			tm=0,
			u=0.0,
			v=0.0,
			w=16.0 * 20.0,
			h=16.0 * 20.0,
		)

		frame_margin = 5
		pyxel.rectb(
			x=frame_margin,
			y=frame_margin,
			w=pyxel.width - 2 * frame_margin,
			h=pyxel.height - 2 * frame_margin,
			col=pyxel.COLOR_WHITE,
		)

		self.player.draw()
		self.ui.draw()


def main() -> None:
	"""
	Point d'entré principal.
	"""
	print("\n# A-Steroid.\n")
	_app = App()

if __name__ == "__main__":
	main()
