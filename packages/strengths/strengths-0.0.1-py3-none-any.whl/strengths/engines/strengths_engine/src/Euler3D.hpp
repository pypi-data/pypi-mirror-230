//implementation using the Euler method

class Euler3D : public SimulationAlgorithm3DBase
    {
    private :

    std::vector<double> mesh_dxdt; //species quantities

    void Compute_dxdt()
        {
        for(int i=0; i<n_meshes; i++)
            {
            //reaction rates
            std::vector<double> rr(n_reactions);

            for(int r=0; r<n_reactions; r++)
                rr[r] = ReactionRate(i, r);

            for(int s=0; s<n_species; s++)
              {
              mesh_dxdt[i*n_species+s] = 0;
              if(mesh_chstt[i*n_species+s]) continue;

              //reaction
              for(int r=0; r<n_reactions; r++)
                {
                mesh_dxdt[i*n_species+s] += sto[s*n_reactions+r]*rr[r];
                }

              //diffusion
              int xcoord = i%w;
              int ycoord = i%(w*h)/w;
              int zcoord = i/(w*h);

              if(xcoord<w-1) mesh_dxdt[i*n_species+s] -= DiffusionRateDifference(i, s, 0);
              if(xcoord>0)   mesh_dxdt[i*n_species+s] -= DiffusionRateDifference(i, s, 1);
              if(ycoord<h-1) mesh_dxdt[i*n_species+s] -= DiffusionRateDifference(i, s, 2);
              if(ycoord>0)   mesh_dxdt[i*n_species+s] -= DiffusionRateDifference(i, s, 3);
              if(zcoord<d-1) mesh_dxdt[i*n_species+s] -= DiffusionRateDifference(i, s, 4);
              if(zcoord>0)   mesh_dxdt[i*n_species+s] -= DiffusionRateDifference(i, s, 5);
              }
            }
        }

    void Apply_dxdt()
        {
        for(int i=0; i<n_meshes; i++)
            {
            for(int j=0; j<n_species; j++)
                {
                mesh_x[i*n_species+j] += mesh_dxdt[i*n_species+j]*dt;
                }
            }
        }

    virtual void AlgorithmSpecificInit()
        {
        this->mesh_dxdt.resize(n_species*n_meshes);
        }

    public :

    Euler3D()
        {
        }

    virtual ~Euler3D()
        {
        }

    virtual bool Iterate()
        {
        Sample();
        if(complete) return false;
        Compute_dxdt();
        Apply_dxdt();
        t += dt;
        return true;
        }

    };
