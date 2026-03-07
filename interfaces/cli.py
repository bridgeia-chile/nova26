"""
CLI Interface
Command line interactions for debugging or local usages.
"""
from rich.console import Console
from rich.markdown import Markdown

class CLIInterface:
    def __init__(self, brain):
        self.brain = brain
        self.console = Console()

    async def start(self):
        import asyncio
        self.console.print("[bold blue]nova26 CLI Iniciada[/bold blue]")
        self.console.print("Escribe 'exit' o 'quit' para salir.")
        
        while True:
            try:
                loop = asyncio.get_running_loop()
                user_input = await loop.run_in_executor(None, self.console.input, "\n[green]Usuario >[/green] ")
                if user_input.lower() in ('exit', 'quit'):
                    break
                
                # Interceptar comandos CLI especiales antes de enviarlos al cerebro
                if user_input.lower() == "/login openai":
                    self.console.print("[dim]Delegando flujo OAuth al Gestor de Autenticación...[/dim]")
                    if hasattr(self.brain, 'oauth_manager'):
                        success = await self.brain.oauth_manager.login_openai()
                        if success:
                            self.console.print("[bold green]Token de OpenAI obtenido. Nova26 ahora puede usar modelos OpenAI (estilo OpenClaw).[/bold green]")
                        else:
                            self.console.print("[bold red]Falló la autenticación con OpenAI.[/bold red]")
                    else:
                        self.console.print("[bold red]Gestor OAuth no disponible en el cerebro de nova26.[/bold red]")
                    continue

                elif user_input.lower() == "/login google":
                    self.console.print("[dim]Delegando flujo OAuth al Gestor de Autenticación (Google)...[/dim]")
                    if hasattr(self.brain, 'oauth_manager'):
                        success = await self.brain.oauth_manager.login_google()
                        if success:
                            self.console.print("[bold green]Token de Google obtenido. Nova26 ahora puede usar modelos Gemini (estilo OpenClaw).[/bold green]")
                        else:
                            self.console.print("[bold red]Falló la autenticación con Google.[/bold red]")
                    else:
                        self.console.print("[bold red]Gestor OAuth no disponible en el cerebro de nova26.[/bold red]")
                    continue

                with self.console.status("[bold yellow]nova26 está pensando y actuando...[/bold yellow]", spinner="dots"):
                    response = await self.brain.process_input(user_input, interface='cli')
                
                self.console.print("\n[bold purple]nova26 >[/bold purple]")
                self.console.print(Markdown(response))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/] {str(e)}")
                
        self.console.print("[yellow]Cerrando CLI...[/yellow]")
