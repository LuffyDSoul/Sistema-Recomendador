"""
Datos Semilla Canónicos del Sistema Recomendador
Extraídos del Trabajo Práctico Integrador:
- 12 Géneros
- 9 Editoriales
- 18 Autores
- 100 Libros reales con páginas, precios y descripciones
- 20 Usuarios
- 22 Preferencias de género (onboarding 0..3)
"""

GENEROS_DATA = [
    {"nombre": "Ciencia Ficción"},
    {"nombre": "Fantasía Épica"},
    {"nombre": "Novela Policial"},
    {"nombre": "Terror y Suspenso"},
    {"nombre": "Desarrollo Personal"},
    {"nombre": "Divulgación Científica"},
    {"nombre": "Historia Universal"},
    {"nombre": "Filosofía"},
    {"nombre": "Realismo Mágico"},
    {"nombre": "Distopía"},
    {"nombre": "Biografía y Memorias"},
    {"nombre": "Tecnología y Software"},
]

EDITORIALES_DATA = [
    {"nombre": "Penguin Random House"},
    {"nombre": "Editorial Planeta"},
    {"nombre": "Minotauro"},
    {"nombre": "Alianza Editorial"},
    {"nombre": "Fondo de Cultura Económica"},
    {"nombre": "Anagrama"},
    {"nombre": "O'Reilly Media"},
    {"nombre": "Tusquets Editores"},
    {"nombre": "Editorial Sudamericana"},
]

AUTORES_DATA = [
    {"nombre": "Isaac Asimov"},
    {"nombre": "J.R.R. Tolkien"},
    {"nombre": "Agatha Christie"},
    {"nombre": "Stephen King"},
    {"nombre": "James Clear"},
    {"nombre": "Carl Sagan"},
    {"nombre": "Yuval Noah Harari"},
    {"nombre": "Friedrich Nietzsche"},
    {"nombre": "Gabriel García Márquez"},
    {"nombre": "George Orwell"},
    {"nombre": "Walter Isaacson"},
    {"nombre": "Robert C. Martin"},
    {"nombre": "Arthur C. Clarke"},
    {"Brandon Sanderson": "Brandon Sanderson"},
    {"nombre": "Brandon Sanderson"},
    {"nombre": "Arthur Conan Doyle"},
    {"nombre": "H.P. Lovecraft"},
    {"nombre": "Jorge Luis Borges"},
    {"nombre": "Martin Fowler"},
]
# Limpiar posible clave incorrecta en autores
AUTORES_DATA = [a for a in AUTORES_DATA if "nombre" in a]

CATALOGO_100_LIBROS = [
    # --- Isaac Asimov (6 libros) ---
    ("Fundación", "Isaac Asimov", "Minotauro", ["Ciencia Ficción"], 256, 18500.0, "Inicio de la saga del Imperio Galáctico y la psicohistoria."),
    ("Fundación e Imperio", "Isaac Asimov", "Minotauro", ["Ciencia Ficción"], 288, 19200.0, "La psicohistoria frente a la impredecible amenaza del Mulo."),
    ("Segunda Fundación", "Isaac Asimov", "Minotauro", ["Ciencia Ficción"], 320, 19800.0, "La búsqueda de la misteriosa colonia de científicos mentales."),
    ("Yo, Robot", "Isaac Asimov", "Alianza Editorial", ["Ciencia Ficción", "Tecnología y Software"], 256, 17000.0, "Relatos seminales que establecen las Tres Leyes de la Robótica."),
    ("Bóvedas de Acero", "Isaac Asimov", "Alianza Editorial", ["Ciencia Ficción", "Novela Policial"], 280, 16500.0, "Un detective humano y un robot investigan un crimen en la Tierra."),
    ("El Sol Desnudo", "Isaac Asimov", "Alianza Editorial", ["Ciencia Ficción", "Novela Policial"], 272, 16900.0, "Baley y Daneel investigan un homicidio en el planeta Solaria."),

    # --- J.R.R. Tolkien (6 libros) ---
    ("El Señor de los Anillos: La Comunidad del Anillo", "J.R.R. Tolkien", "Minotauro", ["Fantasía Épica"], 488, 28500.0, "Frodo Bolsón emprende el viaje para destruir el Anillo Único."),
    ("El Señor de los Anillos: Las Dos Torres", "J.R.R. Tolkien", "Minotauro", ["Fantasía Épica"], 416, 28500.0, "La separación de la Compañía y las guerras en Rohan y Gondor."),
    ("El Señor de los Anillos: El Retorno del Rey", "J.R.R. Tolkien", "Minotauro", ["Fantasía Épica"], 528, 29900.0, "La batalla final por la Tierra Media y el destino del Anillo."),
    ("El Hobbit", "J.R.R. Tolkien", "Minotauro", ["Fantasía Épica"], 310, 21000.0, "La travesía de Bilbo Bolsón junto a los enanos hacia la Montaña Solitaria."),
    ("El Silmarillion", "J.R.R. Tolkien", "Minotauro", ["Fantasía Épica"], 448, 26500.0, "Mitos y leyendas sobre la creación de Arda y las Edades Antiguas."),
    ("Los Hijos de Húrin", "J.R.R. Tolkien", "Minotauro", ["Fantasía Épica"], 320, 22000.0, "Historia trágica de Túrin Turambar ambientada en la Primera Edad."),

    # --- Agatha Christie (6 libros) ---
    ("Diez Negritos", "Agatha Christie", "Editorial Planeta", ["Novela Policial", "Terror y Suspenso"], 224, 15500.0, "Diez personas atrapadas en una isla mueren una a una según una rima infantil."),
    ("Asesinato en el Orient Express", "Agatha Christie", "Editorial Planeta", ["Novela Policial"], 256, 16200.0, "Hércules Poirot resuelve un homicidio a bordo de un tren aislado por la nieve."),
    ("El Asesinato de Roger Ackroyd", "Agatha Christie", "Editorial Planeta", ["Novela Policial"], 288, 16000.0, "Un crimen rural con un giro narrativo revolucionario en la novela policiaca."),
    ("Muerte en el Nilo", "Agatha Christie", "Editorial Planeta", ["Novela Policial"], 336, 17500.0, "Poirot investiga un crimen pasional a bordo de un crucero fluvial."),
    ("Cita con la Muerte", "Agatha Christie", "Editorial Planeta", ["Novela Policial"], 240, 14800.0, "La matriarca de una familia es asesinada durante unas ruinas en Petra."),
    ("El Misterio de la Guía de Ferrocarriles", "Agatha Christie", "Editorial Planeta", ["Novela Policial"], 256, 15900.0, "Un asesino en serie mata víctimas siguiendo el orden alfabético."),

    # --- Stephen King (6 libros) ---
    ("El Resplandor", "Stephen King", "Penguin Random House", ["Terror y Suspenso"], 688, 26000.0, "Una familia cuida un hotel aislado donde fuerzas oscuras acechan."),
    ("It (Eso)", "Stephen King", "Penguin Random House", ["Terror y Suspenso"], 1504, 34000.0, "Un grupo de amigos enfrenta una entidad ancestral que asola su pueblo."),
    ("Misery", "Stephen King", "Penguin Random House", ["Terror y Suspenso"], 400, 21500.0, "Un escritor convaleciente es secuestrado por su fanática número uno."),
    ("Cementerio de Animales", "Stephen King", "Penguin Random House", ["Terror y Suspenso"], 480, 23000.0, "Un antiguo terreno con el poder de resucitar lo enterrado desata horrores."),
    ("Carrie", "Stephen King", "Penguin Random House", ["Terror y Suspenso"], 256, 17500.0, "Una joven marginada descubre sus poderes telequinéticos en el baile escolar."),
    ("Salem's Lot", "Stephen King", "Penguin Random House", ["Terror y Suspenso"], 512, 24000.0, "Un escritor regresa a su pueblo natal y descubre una plaga de vampiros."),

    # --- James Clear (5 libros) ---
    ("Hábitos Atómicos", "James Clear", "Editorial Planeta", ["Desarrollo Personal"], 328, 21000.0, "Método práctico para crear buenos hábitos y eliminar los malos."),
    ("El Poder de los Hábitos Mínimos", "James Clear", "Editorial Planeta", ["Desarrollo Personal"], 210, 16500.0, "Estrategias directas de enfoque e incrementos marginales del 1%."),
    ("Sistemas de Enfoque", "James Clear", "Editorial Planeta", ["Desarrollo Personal"], 220, 17200.0, "Cómo diseñar tu entorno diario para eliminar distracciones persistentes."),
    ("Identidad y Cambio Personal", "James Clear", "Editorial Planeta", ["Desarrollo Personal"], 195, 15800.0, "El rol de las creencias en la consolidación de conductas a largo plazo."),
    ("La Regla del Buen Rendimiento", "James Clear", "Editorial Planeta", ["Desarrollo Personal"], 240, 18000.0, "Optimización de rutinas diarias y persistencia sin agotamiento."),

    # --- Carl Sagan (6 libros) ---
    ("Cosmos", "Carl Sagan", "Editorial Planeta", ["Divulgación Científica"], 448, 27500.0, "Viaje fascinante por el universo, la evolución y la ciencia moderna."),
    ("El Mundo y sus Demonios", "Carl Sagan", "Editorial Planeta", ["Divulgación Científica", "Filosofía"], 496, 28000.0, "La ciencia como una vela en la oscuridad frente al pensamiento mágico."),
    ("Contacto", "Carl Sagan", "Alianza Editorial", ["Ciencia Ficción", "Divulgación Científica"], 432, 23500.0, "Científicos detectan el primer mensaje de inteligencia extraterrestre."),
    ("Un Punto Azul Pálido", "Carl Sagan", "Editorial Planeta", ["Divulgación Científica", "Filosofía"], 416, 26800.0, "Reflexión sobre el futuro y la presencia de la humanidad en el cosmos."),
    ("Los Dragones del Edén", "Carl Sagan", "Alianza Editorial", ["Divulgación Científica"], 288, 19500.0, "Especulaciones fascinantes sobre la evolución de la inteligencia humana."),
    ("Miles de Millones", "Carl Sagan", "Editorial Planeta", ["Divulgación Científica"], 320, 22400.0, "Últimos ensayos de Sagan sobre la vida, el medioambiente y la ciencia."),

    # --- Yuval Noah Harari (5 libros) ---
    ("Sapiens: De animales a dioses", "Yuval Noah Harari", "Penguin Random House", ["Historia Universal", "Filosofía"], 496, 29000.0, "Breve historia de la evolución, revoluciones y destino de la humanidad."),
    ("Homo Deus: Breve historia del mañana", "Yuval Noah Harari", "Penguin Random House", ["Historia Universal", "Tecnología y Software"], 496, 29500.0, "Visión sobre el futuro biotecnológico y la inteligencia artificial."),
    ("21 lecciones para el siglo XXI", "Yuval Noah Harari", "Penguin Random House", ["Filosofía", "Historia Universal"], 400, 26000.0, "Reflexiones sobre los desafíos tecnológicos, políticos y humanos actuales."),
    ("Nexus: Una breve historia de las redes de información", "Yuval Noah Harari", "Penguin Random House", ["Historia Universal", "Tecnología y Software"], 512, 31000.0, "El impacto de las redes de información desde la Edad de Piedra hasta la IA."),
    ("El Fin del Antropoceno", "Yuval Noah Harari", "Penguin Random House", ["Filosofía"], 280, 20500.0, "Ensayos sobre las crisis ecológicas y la gobernanza global futura."),

    # --- Friedrich Nietzsche (5 libros) ---
    ("Así habló Zaratustra", "Friedrich Nietzsche", "Alianza Editorial", ["Filosofía"], 480, 21000.0, "Obra cumbre sobre el Superhombre, la muerte de Dios y el eterno retorno."),
    ("Más allá del bien y del mal", "Friedrich Nietzsche", "Alianza Editorial", ["Filosofía"], 288, 17500.0, "Crítica radical a la moral tradicional y a los filósofos dogmáticos."),
    ("El Anticristo", "Friedrich Nietzsche", "Alianza Editorial", ["Filosofía"], 192, 14000.0, "Examen implacable y condena filosófica del cristianismo institucional."),
    ("La Genealogía de la Moral", "Friedrich Nietzsche", "Alianza Editorial", ["Filosofía"], 224, 16000.0, "Estudio sobre el origen histórico y psicológico de los valores morales."),
    ("El Ocaso de los Ídolos", "Friedrich Nietzsche", "Alianza Editorial", ["Filosofía"], 176, 13500.0, "Filosofar con el martillo contra las grandes ilusiones occidentales."),

    # --- Gabriel García Márquez (6 libros) ---
    ("Cien años de soledad", "Gabriel García Márquez", "Editorial Sudamericana", ["Realismo Mágico"], 496, 27500.0, "La épica historia de la familia Buendía en el mítico pueblo de Macondo."),
    ("El amor en los tiempos del cólera", "Gabriel García Márquez", "Editorial Sudamericana", ["Realismo Mágico"], 496, 26800.0, "La fidelidad y el amor apasionado de Florentino Ariza y Fermina Daza."),
    ("Crónica de una muerte anunciada", "Gabriel García Márquez", "Editorial Sudamericana", ["Novela Policial", "Realismo Mágico"], 160, 15000.0, "Reconstrucción minuciosa de un asesinato que todo el pueblo sabía."),
    ("El coronel no tiene quien le escriba", "Gabriel García Márquez", "Editorial Sudamericana", ["Realismo Mágico"], 120, 13800.0, "La conmovedora espera de la pensión militar por un veterano digno."),
    ("Relato de un náufrago", "Gabriel García Márquez", "Editorial Sudamericana", ["Historia Universal", "Biografía y Memorias"], 176, 14500.0, "Reportaje sobre las desventuras de un marinero diez días en el Caribe."),
    ("Los funerales de la Mamá Grande", "Gabriel García Márquez", "Editorial Sudamericana", ["Realismo Mágico"], 192, 14900.0, "Colección de cuentos que anticipan el universo fantástico de Macondo."),

    # --- George Orwell (5 libros) ---
    ("1984", "George Orwell", "Penguin Random House", ["Distopía", "Ciencia Ficción"], 352, 19500.0, "La lucha de Winston Smith contra el totalitarismo del Gran Hermano."),
    ("Rebelión en la granja", "George Orwell", "Penguin Random House", ["Distopía", "Filosofía"], 144, 14000.0, "Sátira brillante sobre la corrupción del poder y el totalitarismo."),
    ("Homenaje a Cataluña", "George Orwell", "Anagrama", ["Historia Universal", "Biografía y Memorias"], 304, 21000.0, "Crónica personal sobre la Guerra Civil Española y sus facciones."),
    ("Sin blanca en París y Londres", "George Orwell", "Anagrama", ["Biografía y Memorias"], 256, 18500.0, "Relato sobre la vida en la indigencia y los márgenes de las capitales europeas."),
    ("El camino a Wigan Pier", "George Orwell", "Anagrama", ["Historia Universal", "Filosofía"], 288, 19000.0, "Investigación sobre las condiciones de vida de la clase obrera británica."),

    # --- Walter Isaacson (5 libros) ---
    ("Steve Jobs: La Biografía", "Walter Isaacson", "Penguin Random House", ["Biografía y Memorias", "Tecnología y Software"], 640, 32000.0, "Retrato definitivo del visionario cofundador y líder de Apple."),
    ("Leonardo da Vinci", "Walter Isaacson", "Penguin Random House", ["Biografía y Memorias", "Historia Universal"], 608, 31500.0, "Biografía basada en los cuadernos íntimos del genio renacentista."),
    ("Einstein: Su vida y su universo", "Walter Isaacson", "Penguin Random House", ["Biografía y Memorias", "Divulgación Científica"], 704, 33000.0, "La vida y logros del físico más influyente del siglo XX."),
    ("Los Innovadores", "Walter Isaacson", "Penguin Random House", ["Tecnología y Software", "Historia Universal"], 592, 29900.0, "La historia de los pioneros que crearon la computación e Internet."),
    ("El Código de la Vida (Jennifer Doudna)", "Walter Isaacson", "Penguin Random House", ["Divulgación Científica", "Biografía y Memorias"], 544, 30500.0, "La revolución genética de CRISPR y el futuro de la ingeniería médica."),

    # --- Robert C. Martin (Uncle Bob) (5 libros) ---
    ("Clean Code", "Robert C. Martin", "O'Reilly Media", ["Tecnología y Software"], 464, 38000.0, "Manual de buenas prácticas y artesanía en el desarrollo de software."),
    ("The Clean Coder", "Robert C. Martin", "O'Reilly Media", ["Tecnología y Software"], 256, 32000.0, "Código de conducta y profesionalismo para ingenieros de software."),
    ("Clean Architecture", "Robert C. Martin", "O'Reilly Media", ["Tecnología y Software"], 432, 39000.0, "Principios estructurales para diseñar sistemas de software mantenibles."),
    ("Clean Agile", "Robert C. Martin", "O'Reilly Media", ["Tecnología y Software"], 240, 29000.0, "Regreso a los valores y fundamentos originales del Manifiesto Ágil."),
    ("Clean Craftsmanship", "Robert C. Martin", "O'Reilly Media", ["Tecnología y Software"], 380, 35000.0, "Técnicas de TDD, refactorización y diseño evolutivo de software."),

    # --- Arthur C. Clarke (5 libros) ---
    ("2001: Una Odisea Espacial", "Arthur C. Clarke", "Alianza Editorial", ["Ciencia Ficción"], 288, 18500.0, "La expedición hacia Júpiter junto al superordenador HAL 9000."),
    ("Cita con Rama", "Arthur C. Clarke", "Alianza Editorial", ["Ciencia Ficción"], 256, 17900.0, "Exploración de un enigmático cilindro alienígena en el sistema solar."),
    ("El Fin de la Infancia", "Arthur C. Clarke", "Alianza Editorial", ["Ciencia Ficción", "Filosofía"], 272, 17500.0, "Los Superseñores descienden a la Tierra para guiar una nueva evolución."),
    ("Fuentes del Paraíso", "Arthur C. Clarke", "Alianza Editorial", ["Ciencia Ficción"], 320, 19000.0, "El reto ingenieril de construir el primer ascensor espacial de la Tierra."),
    ("La Ciudad y las Estrellas", "Arthur C. Clarke", "Alianza Editorial", ["Ciencia Ficción"], 304, 18200.0, "El despertar del último humano en una megaciudad inmortal milenaria."),

    # --- Brandon Sanderson (6 libros) ---
    ("El Imperio Final (Nacidos de la Bruma 1)", "Brandon Sanderson", "Minotauro", ["Fantasía Épica"], 688, 27500.0, "Kelsier y Vin planean derrocar al tirano inmortal en Scadrial."),
    ("El Pozo de la Ascensión (Nacidos de la Bruma 2)", "Brandon Sanderson", "Minotauro", ["Fantasía Épica"], 784, 28900.0, "Las consecuencias políticas tras la caída de un imperio milenario."),
    ("El Héroe de las Eras (Nacidos de la Bruma 3)", "Brandon Sanderson", "Minotauro", ["Fantasía Épica"], 768, 29500.0, "La batalla climática para salvar el planeta de la destrucción total."),
    ("El Camino de los Reyes", "Brandon Sanderson", "Minotauro", ["Fantasía Épica"], 1200, 39500.0, "Inicio monumental de El Archivo de las Tormentas en Roshar."),
    ("Palabras Radiantes", "Brandon Sanderson", "Minotauro", ["Fantasía Épica"], 1248, 41000.0, "El resurgimiento de los Caballeros Radiantes contra el Vacío."),
    ("El Aliento de los Dioses", "Brandon Sanderson", "Minotauro", ["Fantasía Épica"], 704, 28000.0, "Magia fundamentada en colores, alientos bio-cromáticos e intrigas divinas."),

    # --- Arthur Conan Doyle (5 libros) ---
    ("Estudio en Escarlata", "Arthur Conan Doyle", "Alianza Editorial", ["Novela Policial"], 192, 14000.0, "Primera aventura y encuentro entre Sherlock Holmes y el Dr. Watson."),
    ("El Sabueso de los Baskerville", "Arthur Conan Doyle", "Alianza Editorial", ["Novela Policial", "Terror y Suspenso"], 256, 16500.0, "Una bestia diabólica acecha a los herederos en los páramos de Dartmoor."),
    ("El Signo de los Cuatro", "Arthur Conan Doyle", "Alianza Editorial", ["Novela Policial"], 208, 14800.0, "Misterio que involucra un tesoro robado en la India y pactos secretos."),
    ("Las Aventuras de Sherlock Holmes", "Arthur Conan Doyle", "Alianza Editorial", ["Novela Policial"], 368, 18500.0, "Colección de los casos más famosos resueltos desde Baker Street."),
    ("El Valle del Terror", "Arthur Conan Doyle", "Alianza Editorial", ["Novela Policial"], 240, 15500.0, "Holmes descubre los tentáculos criminales del Profesor Moriarty."),

    # --- H.P. Lovecraft (6 libros) ---
    ("La Llamada de Cthulhu", "H.P. Lovecraft", "Alianza Editorial", ["Terror y Suspenso"], 160, 13500.0, "Relatos fundacionales sobre dioses primigenios y horrores cósmicos."),
    ("En las Montañas de la Locura", "H.P. Lovecraft", "Alianza Editorial", ["Terror y Suspenso", "Ciencia Ficción"], 224, 15800.0, "Una expedición antártica halla vestigios de una civilización no humana."),
    ("La Sombra sobre Innsmouth", "H.P. Lovecraft", "Alianza Editorial", ["Terror y Suspenso"], 176, 14200.0, "Los oscuros secretos marítimos y pactos de un decrépito pueblo costero."),
    ("El Horror de Dunwich", "H.P. Lovecraft", "Alianza Editorial", ["Terror y Suspenso"], 192, 14500.0, "Una criatura invisible y monstruosa crece encerrada en una granja aislada."),
    ("El Color que Cayó del Cielo", "H.P. Lovecraft", "Alianza Editorial", ["Terror y Suspenso", "Ciencia Ficción"], 180, 14000.0, "Un meteorito infecta el suelo y enloquece a los habitantes de un valle."),
    ("El Caso de Charles Dexter Ward", "H.P. Lovecraft", "Alianza Editorial", ["Terror y Suspenso"], 240, 16000.0, "Nigromancia, resurrecciones prohibidas y locura en Nueva Inglaterra."),

    # --- Jorge Luis Borges (6 libros) ---
    ("Ficciones", "Jorge Luis Borges", "Editorial Sudamericana", ["Realismo Mágico", "Filosofía"], 224, 21000.0, "Laberintos, bibliotecas infinitas y espejos en relatos fundamentales."),
    ("El Aleph", "Jorge Luis Borges", "Editorial Sudamericana", ["Realismo Mágico", "Filosofía"], 208, 21000.0, "Cuentos sobre la eternidad, el infinito y un punto con todos los puntos."),
    ("El Libro de Arena", "Jorge Luis Borges", "Editorial Sudamericana", ["Realismo Mágico", "Filosofía"], 192, 19500.0, "Un libro con páginas infinitas y objetos que desafían la realidad."),
    ("Historia Universal de la Infamia", "Jorge Luis Borges", "Editorial Sudamericana", ["Realismo Mágico", "Historia Universal"], 176, 18000.0, "Reinvenciones líricas de crímenes e impostores históricos célebres."),
    ("El Informe de Brodie", "Jorge Luis Borges", "Editorial Sudamericana", ["Realismo Mágico"], 160, 17500.0, "Relatos directos sobre compadritos, duelos de cuchilleros y destinos."),
    ("Inquisiciones", "Jorge Luis Borges", "Editorial Sudamericana", ["Filosofía"], 240, 19800.0, "Ensayos agudos sobre la literatura clásica, metafísica y el lenguaje."),

    # --- Martin Fowler (6 libros) ---
    ("Refactoring: Improving the Design of Existing Code", "Martin Fowler", "O'Reilly Media", ["Tecnología y Software"], 448, 42000.0, "La guía definitiva para reestructurar código sin alterar su comportamiento."),
    ("Patterns of Enterprise Application Architecture", "Martin Fowler", "O'Reilly Media", ["Tecnología y Software"], 560, 45000.0, "Patrones clásicos para estructurar capas en sistemas de gestión empresarial."),
    ("UML Distilled", "Martin Fowler", "O'Reilly Media", ["Tecnología y Software"], 192, 26000.0, "Guía concisa del lenguaje unificado de modelado para desarrolladores."),
    ("Domain-Specific Languages", "Martin Fowler", "O'Reilly Media", ["Tecnología y Software"], 640, 44000.0, "Diseño e implementación de lenguajes orientados a dominios de negocio."),
    ("Building Microservices Principles", "Martin Fowler", "O'Reilly Media", ["Tecnología y Software"], 310, 34000.0, "Fundamentos de integración y descentralización en arquitecturas distribuidas."),
    ("Continuous Delivery Pipelines", "Martin Fowler", "O'Reilly Media", ["Tecnología y Software"], 350, 36000.0, "Automatización de despliegues seguros y pipelines de entrega continua."),
]

USUARIOS_DATA = [
    {"nombre": "Emiliano Lanaro", "email": "emilianolanaro@gmail.com", "password": "mequebrelaclavicula"},
    {"nombre": "Pablo Leal", "email": "pabloleal@gmail.com", "password": "noconozcolaluzdelsol"},
    {"nombre": "Ignacio Martinez", "email": "ignaciomartinez912@gmail.com", "password": "goldemartinez"},
    {"nombre": "Valentin Schultheis", "email": "valentinschultheis@gmail.com", "password": "morienmadrid"},
    {"nombre": "Giovanni Rottoli", "email": "giorottoli@gmail.com", "password": "cienciadedatos1"},
    {"nombre": "Lia Aguirre", "email": "liaaguirre@gmail.com", "password": "cienciadedatos2"},
    {"nombre": "Lionel Messi", "email": "leomessi1812@gmail.com", "password": "8bdo"},
    {"nombre": "Rodrigo De Paul", "email": "messiteamo@gmail.com", "password": "messiteamo"},
    {"nombre": "Claudio Tapia", "email": "chiquitapia12@gmail.com", "password": "aguanteboca"},
    {"nombre": "Mark Zuckerberg", "email": "markzuckerberg@gmail.com", "password": "terobolosdatos"},
    {"nombre": "Angel Correa", "email": "angelcorrea@gmail.com", "password": "elultimo10"},
    {"nombre": "Thiago Almada", "email": "thiagoalmada@gmail.com", "password": "fulbochampan"},
    {"nombre": "Geronimo Benavides", "email": "geromomo@gmail.com", "password": "trespropiedades"},
    {"nombre": "Malcom Braida", "email": "malcombraida@gmail.com", "password": "peine123"},
    {"nombre": "Ulises Rapallini", "email": "ulisesrapallini@gmail.com", "password": "aguantelaia"},
    {"nombre": "Elon Musk", "email": "elonmusk@gmail.com", "password": "vivaspacex"},
    {"nombre": "Valentin Barco", "email": "colobarco@gmail.com", "password": "scalonidejamejugar"},
    {"nombre": "Santiago Grizas", "email": "santigrizas19@gmail.com", "password": "riverplate"},
    {"nombre": "David Quint", "email": "davoxeneixe@gmail.com", "password": "yotambienmorienmadrid"},
    {"nombre": "Lautaro Del Campo", "email": "lacobra@gmail.com", "password": "quieroqueque"}
]

USUARIOS_GENEROS_NOMBRES = {
    "pabloleal@gmail.com": ["Ciencia Ficción", "Terror y Suspenso", "Historia Universal"],
    "emilianolanaro@gmail.com": ["Fantasía Épica", "Desarrollo Personal"],
    "ulisesrapallini@gmail.com": ["Novela Policial", "Filosofía"],
    "leomessi1812@gmail.com": ["Ciencia Ficción"],
    "messiteamo@gmail.com": ["Ciencia Ficción", "Fantasía Épica"],
    "markzuckerberg@gmail.com": ["Realismo Mágico"],
    "elonmusk@gmail.com": ["Realismo Mágico", "Distopía"],
    "liaaguirre@gmail.com": ["Terror y Suspenso", "Divulgación Científica"],
    "ignaciomartinez912@gmail.com": ["Fantasía Épica", "Novela Policial"],
    "davoxeneixe@gmail.com": ["Desarrollo Personal"],
    "chiquitapia12@gmail.com": ["Ciencia Ficción", "Distopía"],
    "santigrizas19@gmail.com": ["Novela Policial", "Historia Universal"]
}
