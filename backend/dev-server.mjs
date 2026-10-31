// Runs the same-origin local workbench; accepts common dev-server host/port flags.
import{spawn}from'node:child_process';
const args=process.argv.slice(2);const option=(name,fallback)=>{let i=args.indexOf(name);return i>=0?args[i+1]:fallback};
const python=process.env.GEOTWIN_PYTHON||process.env.CODEX_PRIMARY_RUNTIME_PYTHON||'python3';
const child=spawn(python,['-m','uvicorn','backend.dev:app','--host',option('--host','127.0.0.1'),'--port',option('--port',process.env.PORT||'4173')],{stdio:'inherit',env:process.env});
child.on('error',e=>{console.error('Cannot start Python. Set GEOTWIN_PYTHON to the Python environment where backend/requirements.txt is installed. '+e.message);process.exit(1)});child.on('exit',code=>process.exit(code??1));for(let sig of ['SIGTERM','SIGINT'])process.on(sig,()=>child.kill(sig));
