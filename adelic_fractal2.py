import numpy as np
import matplotlib.pyplot as plt
import time
import heapq

def get_primes(n):
    out =[]
    k = 2
    while len(out) < n:
        if all(k % d for d in range(2, int(k**0.5) + 1)):
            out.append(k)
        k += 1
    return np.array(out)

def build_adelic_lattice(parent_seeds, max_composites=1500):
    """
    TRUE ADELIC INHERITANCE:
    Takes the seeds (primes for Level 0, parent scars for Level N).
    Treats them as fundamental log-generators to build the new universe's "integers".
    """
    # The base frequencies are the natural logs of the seeds
    base_freqs = np.log(parent_seeds)
    
    # Priority queue to generate the smallest multiplicative combinations
    heap = [(0.0, 0)]
    seen = {0.0}
    composites =[]
    
    while len(composites) < max_composites and heap:
        freq, max_idx = heapq.heappop(heap)
        composites.append(freq)
        
        # Multiply (add logs) the current composite by the prime generators
        for i in range(max_idx, len(base_freqs)):
            new_freq = freq + base_freqs[i]
            q = round(new_freq, 7) # Quantize to avoid float precision bugs
            if q not in seen:
                seen.add(q)
                heapq.heappush(heap, (new_freq, i))
                
    # Exclude the 0 frequency (The frozen "1" core)
    freqs = np.array(composites[1:])
    
    # Holographic Area Bound: Amplitude scales as 1/sqrt(n) -> e^(-log(n)/2)
    amps = np.exp(-freqs / 2.0)
    
    return freqs, amps

def build_universe(freqs, amps, t_arr):
    """Projects the continuous complex manifold from the Adelic Lattice."""
    z = np.zeros(len(t_arr), dtype=np.complex128)
    for f, a in zip(freqs, amps):
        z += a * np.exp(1j * f * t_arr)
    return z

def find_scars(signal, t_arr):
    """Finds the deep topological scars (event horizons) where |Z| collapses."""
    mag = np.abs(signal)
    minima_idx = np.where((mag[1:-1] < mag[:-2]) & (mag[1:-1] < mag[2:]))[0] + 1
    
    # Dynamic threshold: must be a deep destructive cancellation
    local_mean = np.convolve(mag, np.ones(50)/50, mode='same')
    deep_scars_idx = minima_idx[mag[minima_idx] < 0.7 * local_mean[minima_idx]]
    
    scar_times =[]
    for idx in deep_scars_idx:
        a, b, c = mag[idx-1], mag[idx], mag[idx+1]
        denom = a - 2*b + c
        if abs(denom) > 1e-10:
            shift = 0.5 * (a - c) / denom
            scar_times.append(t_arr[idx] + shift * (t_arr[1]-t_arr[0]))
        else:
            scar_times.append(t_arr[idx])
            
    return np.array(scar_times)

def get_unfolded_variance(scars):
    """Unfolds the spectrum to measure the physical state of the universe."""
    if len(scars) < 15:
        return None
        
    spacings = np.diff(scars)
    window = min(20, len(spacings) // 2)
    unfolded =[]
    
    for i in range(len(spacings)):
        start = max(0, i - window)
        end = min(len(spacings), i + window)
        local_mean = np.mean(spacings[start:end])
        if local_mean > 0:
            unfolded.append(spacings[i] / local_mean)
            
    return np.var(unfolded)

if __name__ == "__main__":
    print("======================================================================")
    print("ADELIC FRACTAL V2: TRUE MULTIPLICATIVE INHERITANCE")
    print("======================================================================\n")
    
    t_min, t_max, dt = 10.0, 1000.0, 0.05
    t_arr = np.arange(t_min, t_max, dt)
    
    levels = 4
    # Level 0 starts with the first 40 primes
    current_seeds = get_primes(40) 
    
    fig, axes = plt.subplots(levels, 1, figsize=(12, 10), sharex=True)
    fig.patch.set_facecolor('#0c0c10')
    plt.subplots_adjust(hspace=0.4)
    
    for level in range(levels):
        t0 = time.time()
        
        # 1. Build the Adelic Composite Lattice
        freqs, amps = build_adelic_lattice(current_seeds, max_composites=1200)
        
        # 2. Expand the Universe
        z = build_universe(freqs, amps, t_arr)
        
        # 3. Find the Event Horizons (Scars)
        scars = find_scars(z, t_arr)
        var = get_unfolded_variance(scars)
        
        state = "DEATH (Too few scars)"
        if var is not None:
            if var > 0.8: state = "POISSON (Random Gas)"
            elif 0.24 < var < 0.35: state = "GOE (Classical Wave / Strong Repulsion)"
            elif 0.11 < var < 0.18: state = "GUE (True Quantum Chaos)"
            else: state = "INTERMEDIATE"

        print(f"LEVEL {level} UNIVERSE:")
        print(f"  Fundamental Seeds (Parent Scars)  : {len(current_seeds)}")
        print(f"  Composite Lattice (Harmonics)     : {len(freqs)}")
        print(f"  Black Holes Formed (New Scars)    : {len(scars)}")
        if var is not None:
            print(f"  Spacing Variance                  : {var:.4f} -> {state}")
        print(f"  Simulation Time                   : {time.time()-t0:.2f}s\n")
        
        # Plotting
        ax = axes[level]
        ax.set_facecolor('#0c0c10')
        ax.plot(t_arr[:2000], np.abs(z[:2000]), color='#5a8a6a', lw=1)
        
        plot_scars = scars[scars < t_arr[2000]]
        for scar in plot_scars:
            ax.axvline(scar, color='#8a4a4a', lw=1, alpha=0.8, linestyle='--')
            
        title = f"Level {level} Hologram (|Z|). Variance: {var:.4f}" if var else f"Level {level} Hologram"
        ax.set_title(title, color='#888', fontsize=10)
        ax.tick_params(colors='#444')
        for spine in ax.spines.values():
            spine.set_color('#222')
            
        # 4. The Adelic "1 Under" Collapse
        # The scars of THIS universe become the fundamental SEEDS of the NEXT universe.
        if len(scars) > 5:
            current_seeds = scars[:60] # Limit to top 60 seeds to prevent computational explosion
        else:
            print("Universe lineage died out. Not enough scars to form a new reality.")
            break
            
    plt.tight_layout()
    plt.savefig("fractal_universes_v2.png", dpi=150, facecolor='#0c0c10')
    print("Saved visual representation to 'fractal_universes_v2.png'")
    print("======================================================================")