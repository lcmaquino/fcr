## Descrição

O programa Fenix Controlador de Ressolda (FCR) controla a temperatura de dois
dispositivos de aquecimento para a realização de pré-aquecimento de placas 
eletrônicas ou para a ressoldagem de componentes BGA. Como exemplo de 
dispositivo de aquecimento pode-se citar uma churrasqueira elétrica ou 
uma resitência elétrica. Devido a alta corrente elétrica necessária para 
ligar esses dispositivos, eles devem ser acionados via um relê mecânico 
ou um relê de estado sólido.

O FCR é composto por um circuito eletrônico com o microcontrolador
[Raspberry Pi Pico](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)
e por um conjunto de códigos escritos para [MicroPython](https://www.micropython.org/).

## Montagem e Instalação

  - Monte o circuito eletrônico conforme o diagrama esquemático:
  [fenix-controlador-de-ressolda.pdf](https://github.com/lcmaquino/fcr/tree/main/pcb/fenix-controlador-de-ressolda.pdf);
  - Conecte os pinos de entrada do relê nos conectores indicados no diagrama 
  por `OUT1` e `OUT2`;
  - Conecte os pinos de saída do relê nos dispositivos de aquecimento;
  - Conecte os módulos HD44780 LCD 16×02, MAX6675 e Keyes_AD_Key nos seus respectivos
    conectores indicados no diagrama;
  - Instale o [firmware do MicroPython](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3) 
  no Raspberry Pi Pico;
  - Utilize a sua IDE preferida para copiar todos os arquivos do diretório 
  [`src`](https://github.com/lcmaquino/fcr/tree/main/src) para o Raspberry Pi Pico.
  (Por exemplo, você pode usar o [Thonny](https://thonny.org/) ou o 
  [Visual Studio Code](https://code.visualstudio.com/));
  - Ligue o circuito eletrônico com uma fonte de alimentação de 5V DC e 
  pelo menos 500mA;

  O módulo Keyes_AD_Key possui cinco chaves tácteis rotuladas como SW1, SW2, 
  SW3, SW4 e SW5. O FCR faz o mapeamento dessas chaves para a navegação 
  dos menus de modo que:

  - SW1 - movimenta o menu para a esquerda;
  - SW2 - aumenta o valor da opção exibida no momento;
  - SW3 - diminui o valor da opção exibida no momento;
  - SW4 - movimenta o menu para a direita;
  - SW5 - seleciona o menu atual;

## Uso

  O FCR possui três modos:
  - Preheater - para realizar o pré-aquecimento de uma placa eletrônica;
  - Reballing - para realizar a ressolda de componentes BGA;
  - Auto Tuning - para calcular automaticamente os parâmetros usados no controle
  [PID](https://pt.wikipedia.org/wiki/Controlador_proporcional_integral_derivativo);

  Todos os modos possuem um menu que contém opções específicas e opções gerais.

  As opções gerais são:
  - `Kp` - coeficiente proporcional do controle PID;
  - `Ki` - coeficiente integral do controle PID;
  - `Kd` - coeficiente derivativo do controle PID;
  - `ap` - _actuation period_ é o período (em segundos) no qual o controle PID é atualizado;
  - `Run` - executar as funções do modo;
  - `Home` - voltar para a tela inicial de seleção de modo;

  Vide a seguir as opções específicas de cada modo.

### Modo Preheater

  O modo Preheater controla apenas um dispositivo de aquecimento que deve ser 
  posicionado abaixo da placa eletrônica.

  No modo Preheater as opções específicas são:
  - `SV` - _Setpoint Variable_ é a temperatura (em graus Celcius) que o 
    elemento de aquecimento deve atingir;
  - `d` - _duration_ é a duração (em segundos) que o modo deve ficar executando;

### Modo Reballing

  O modo Reballing controla dois dispositivos de aquecimento sendo que 
  um deles deve ser posicionado abaixo da placa eletrônica e o outro
  acima dela.

  No modo Reballing as opções específicas são:
  - `PTN` - _pattern_ é o padrão de temperatura (em graus Celcius) 
    que os dispositivos de aquecimento devem seguir. Cada padrão é composto por até cinco 
    partes, sendo que cada uma delas contém as opções `r`, `L` e `d` explicadas a seguir;
  - `r` - _rate_ é a taxa de variação da temperatura (em graus Celcius por segundo);
  - `L` - _limit_ é o valor limite que a temperatura (em graus Celcius) deve atingir;
  - `d` - _duration_ é a duração (em segundos) que a temperatura deve permanecer no seu limite `L`;

  É possível configurar até 10 padrões de temperatura. Veja um exemplo de configuração a seguir:
```
  PTN1
  | - r1: 0.86
  | - L1: 120.0
  | - d1: 60
  | - r2: 0.57
  | - L2: 180.0
  | - d2: 60
  | - r3: 0.29
  | - L3: 210.0
  | - d3: 60
  | - r4: 0.19
  | - L4: 227.0
  | - d4: 60
  | - r5: 0.0
  | - L5: 0.0
  | - d5: 0
```

  Note que nesse exemplo o padrão PTN1 terá quatro partes ativas. A quinta parte
  está toda nula e será ignorada pelo FCR. A figura a seguir representa esse padrão.

  ![Imagem do gráfico representando o padrão PTN1](https://github.com/lcmaquino/fcr/blob/main/assets/plot_ptn1.svg)

  Na primeira parte do padrão a temperatura deverá
  subir com uma taxa de variação de `r1 = 0.86`°C/s até atingir `L1 = 120`°C, 
  ficando nessa temperatura por `d1 = 60`s. Na segunda parte a temperatura deverá
  subir com uma taxa de variação de `r2 = 0.57`°C/s até atingir `L2 = 180`°C, 
  ficando nessa temperatura por `d2 = 60`s. Já na terceira parte a temperatura 
  deverá subir com uma taxa de variação de `r3 = 0.29`°C/s até atingir `L3 = 210`°C, 
  ficando nessa temperatura por `d3 = 60`s. Por fim, na quarta parte a temperatura 
  deverá subir com uma taxa de variação de `r4 = 0.19`°C/s até atingir `L4 = 227`°C, 
  ficando nessa temperatura por `d4 = 60`s.

### Auto Tuning

  O modo Auto Tuning analisa os dados de temperatura do dispostivo de aquecimento 
  abaixo da placa eletrônica para calcular de modo aproximado os coeficientes
  `Kp`, `Ki` e `Kd` do controlador PID.

  No modo Auto Tuning as opções específicas são:
  - `SV` - _Setpoint Variable_ é a temperatura (em graus Celcius) que o 
    elemento de aquecimento deve atingir;
  - `d` - _duration_ é a duração (em segundos) que o modo deve ficar executando;

## Licença

FCR é um programa de código aberto sob a licença [GPL v3.0 ou posterior](https://github.com/lcmaquino/ccolab/blob/main/LICENSE).
