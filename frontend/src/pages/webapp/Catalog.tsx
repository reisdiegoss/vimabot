import React, { useEffect } from 'react';

const WebAppCatalog: React.FC = () => {
    useEffect(() => {
        // Inicializa o Telegram WebApp SDK se disponível
        const tg = (window as any).Telegram?.WebApp;
        if (tg) {
            tg.expand();
            tg.ready();
        }
    }, []);

    return (
        <div className="min-h-screen bg-netflix-black text-white p-4">
            <header className="flex items-center justify-between py-4 border-b border-white/10 mb-6">
                <div className="text-netflix-red font-black text-xl tracking-tighter">VimaBOT</div>
                <div className="h-8 w-8 rounded-full bg-slate-800" />
            </header>

            <main className="space-y-8">
                <section>
                    <h2 className="text-lg font-bold mb-4">Destaques para Você</h2>
                    <div className="flex gap-4 overflow-x-auto hide-scrollbar pb-4">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="min-w-[140px] aspect-[2/3] bg-slate-900 rounded-md shadow-lg" />
                        ))}
                    </div>
                </section>
            </main>
        </div>
    );
};

export default WebAppCatalog;
