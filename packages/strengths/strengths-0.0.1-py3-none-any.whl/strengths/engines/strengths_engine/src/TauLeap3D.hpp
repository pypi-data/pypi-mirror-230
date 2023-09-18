//implementation using the Gillespie algorithm with the tau-leap approximation

// #######################################################################################
// the tau leap algorithm.
// reference :
// Gillespie, D. T. (2001). Approximate accelerated stochastic simulation of chemically reacting systems.
// The Journal of Chemical Physics, 115(4), 1716-1733. https://doi.org/10.1063/1.1378322
// #######################################################################################

class TauLeap3D : public SimulationAlgorithm3DBase
    {
    private :

    std::vector<int> mesh_nr; //species quantities
    std::vector<int> mesh_nd; //species quantities

    void Compute_nevt()
        {
        for(int i=0; i<n_meshes; i++)
            {
            //reaction rates
            for(int r=0; r<n_reactions; r++)
                mesh_nr[i*n_reactions+r] = Poisson(ReactionProp(i, r)*dt);

            for(int s=0; s<n_species; s++)
                {
                //diffusion
                for(int n=0;n<6;n++)
                    mesh_nd[i*6*n_species+s*6+n] = 0;

                int xcoord = i%w;
                int ycoord = i%(w*h)/w;
                int zcoord = i/(w*h);

                if(xcoord<w-1) mesh_nd[i*6*n_species+s*6+0] = Poisson(DiffusionProp(i, s, 0)*dt);
                if(xcoord>0)   mesh_nd[i*6*n_species+s*6+1] = Poisson(DiffusionProp(i, s, 1)*dt);
                if(ycoord<h-1) mesh_nd[i*6*n_species+s*6+2] = Poisson(DiffusionProp(i, s, 2)*dt);
                if(ycoord>0)   mesh_nd[i*6*n_species+s*6+3] = Poisson(DiffusionProp(i, s, 3)*dt);
                if(zcoord<d-1) mesh_nd[i*6*n_species+s*6+4] = Poisson(DiffusionProp(i, s, 4)*dt);
                if(zcoord>0)   mesh_nd[i*6*n_species+s*6+5] = Poisson(DiffusionProp(i, s, 5)*dt);
                }
            }
        }

    void Apply_nevt()
        {
        for(int i=0; i<n_meshes; i++)
            {
            for(int r=0; r<n_reactions; r++)
              {
              for(int j=0; j<n_species; j++)
                {
                if(mesh_chstt[i*n_species+j]) continue;
                mesh_x[i*n_species+j] += sto[j*n_reactions+r]*mesh_nr[i*n_reactions+r];
                }
              }

            for(int s=0; s<n_species; s++)
                {
                for (int n=0; n<6; n++)
                    {
                    if(mesh_nd[i*6*n_species+s*6+n]==0) continue;

                    if(! mesh_chstt[i*n_species+s])
                        {
                        mesh_x[i*n_species+s] -= mesh_nd[i*6*n_species+s*6+n];
                        }
                    int ni = i + delta_i[n];
                    if(! mesh_chstt[ni*n_species+s])
                        {
                        mesh_x[ni*n_species+s] += mesh_nd[i*6*n_species+s*6+n];
                        }
                    }
                }
            }
        }

    virtual void AlgorithmSpecificInit()
        {
        this->mesh_nr.resize(n_reactions*n_meshes);
        this->mesh_nd.resize(6*n_species*n_meshes);
        }

    public :

    TauLeap3D()
        {
        }

    virtual ~TauLeap3D()
        {
        }

    virtual bool Iterate()
        {
        Sample();
        if(complete) return false;
        Compute_nevt();
        Apply_nevt();
        t += dt;
        return true;
        }
    };
