//implements the base for the 3D kinetics simulation algorithms

class SimulationAlgorithm3DBase
    {
    protected :

    int w, h, d, n_meshes;                          // system dimensions and number of meshes
    int n_species, n_reactions, n_env;              // number of species, number of reactions// N=n_species, M=n_reactions
    std::vector<int> delta_i;                       // mesh index offset associated with each of the 6 directions
    std::vector<int> opposed_direction;             // opposed direction index
    std::vector<double> mesh_x;                     // species quantities
    std::vector<int> mesh_chstt;                    // chemostates
    std::vector<int> mesh_env;                      // chemostates
    double mesh_vol;                                // mesh volume
    std::vector<double> sto;                        // reaction species change stoechiometry matrix
    std::vector<double> sub;                        // substrates stroechiometry matrix
    std::vector<double> mesh_kr;                    // reaction kinetic rates (accounting for mesh volumes)//n_meshes * n_reactions
    std::vector<double> mesh_kd;                    // diffusion kinetic rates //n_species * n_meshes * n_meshes
    int n_samples;                                  // size of t_samples
    int sample_pos;                                 // index of the next sample time
    std::vector<double> t_samples;                  // sample timepoints
    std::vector<std::vector<double>> sample_mesh_x; // sample_n states successivly sampled.
    double t;                                       // time
    double dt;                                      // time step
    bool complete;                                  // true if all the sampling is done.
    std::mt19937 rng;                               // pseudo random number generator
    std::uniform_real_distribution<double> uiud;    // floating point uniform distribution in [0,1[

    int Poisson(double lambda)
        {
        return std::poisson_distribution<int>(lambda)(rng);
        }

    bool AreNeighbors(int i, int j)
    // returns true if meshes i and j are neighbors. false ohterwise
        {
        int xi = i%w;
        int yi = i%(w*h)/w;
        int zi = i/(w*h);

        int xj = j%w;
        int yj = j%(w*h)/w;
        int zj = j/(w*h);

        return ((abs(xi-xj)+abs(yi-yj)+abs(zi-zj)) == 1);
        }

    void Build_mesh_kr(const std::vector<double> & k, const std::vector<int> & r_env)
    // builds mesh_kr
        {
        mesh_kr.clear();
        mesh_kr.resize(n_meshes*n_reactions, 0);
        for(int i=0;i<n_meshes;i++)
          {
          for(int r=0; r<n_reactions; r++)
            {
            int q = 0;
            for(int s=0; s<n_species; s++)
                q+=sub[s*n_reactions+r];
            mesh_kr[i*n_reactions+r] = k[r]*pow(mesh_vol,1-q)*r_env[r*n_env+mesh_env[i]];
            }
          }
        }

    void Build_mesh_kd(const std::vector<double> & D)
    // builds mesh_kd
        {
        mesh_kd.clear();
        mesh_kd.resize(n_species*n_meshes*6, 0);
        for(int s=0;s<n_species;s++)
            {
            for(int i=0;i<n_meshes;i++)
                {
                for(int n=0; n<6; n++)
                    {
                    int j = i + delta_i[n];

                    int xcoord = j%w;
                    int ycoord = j%(w*h)/w;
                    int zcoord = j/(w*h);
                    if(xcoord>w-1 || xcoord<0 || ycoord>h-1 || ycoord<0 || zcoord>d-1 || zcoord<0)
                        {
                        mesh_kd[i*n_species*6 + s*6+ n] = 0;
                        continue;
                        }

                    // #########################################################################
                    // diffusion reaction rate constants are calculated according to David Bernstein's method.
                    // reference :
                    // Bernstein, D. (2005). Simulating mesoscopic reaction-diffusion systems using the Gillespie algorithm.
                    // Physical Review E, 71(4), Article 041103. https://doi.org/10.1103/PhysRevE.71.041103
                    double hi = pow(mesh_vol, 1.0/3.0);
                    double hj = pow(mesh_vol, 1.0/3.0);
                    double Di = D[s*n_env+mesh_env[i]];
                    double Dj = D[s*n_env+mesh_env[j]];
                    double Dij = (hi + hj)/(hi/Di+hj/Dj);

                    mesh_kd[i*n_species*6 + s*6+ n] = Dij/(hi*(hi+hj)/2);
                    // #########################################################################
                    }
                }
            }
        }

    void CompleteSampling()
    // samples the current state for the remaining sample times, and flags the simulation as complete
        {
        for(;;)
            {
            sample_mesh_x.push_back(mesh_x);
            sample_pos ++;
            if (sample_pos == n_samples)
                {
                complete = true;
                break;
                }
            }
        }

    void Sample()
    // samples the current state for all sample times inferior to t.
        {
        while(t>=t_samples[sample_pos])
            {
            sample_mesh_x.push_back(mesh_x);
            sample_pos ++;
            if (sample_pos == n_samples)
                {
                complete = true;
                break;
                }
            }
        }

    double ReactionRate(int mesh_index, int reaction_index)
    // computes the deterministic reaction rate
        {
        double r = mesh_kr[mesh_index*n_reactions+reaction_index];
        for(int s=0; s<n_species; s++)
            r *= pow(mesh_x[mesh_index*n_species+s], sub[s*n_reactions+reaction_index]);
        return r;
        }

    double ReactionProp(int mesh_index, int reaction_index)
    // computes the Gillespie reaction propensity
        {
        // #######################################################################################
        // reactions propensities for the Gillespie algorithm.
        // reference :
        // Gillespie, D. T. (1977). Exact stochastic simulation of coupled chemical reactions.
        // The Journal of Physical Chemistry, 81(25), 2340-2361. https://doi.org/10.1021/j100540a008
        double a = mesh_kr[mesh_index*n_reactions+reaction_index];
        for(int s = 0; s<n_species; s++)
            {
            if (mesh_x[mesh_index*n_species+s] >= sub[s*n_reactions+reaction_index])
                {
                for (int q=0;q<sub[s*n_reactions+reaction_index];q++)
                    {
                    a *= (mesh_x[mesh_index*n_species+s]-q);
                    }
                }
            else
                {
                a = 0;
                break;
                }
            }
        return a;
        // #######################################################################################
        }

    double DiffusionRate(int mesh_index, int species_index, int direction)
        {
        return mesh_x[mesh_index*n_species+species_index] * mesh_kd[mesh_index*n_species*6+species_index*6+direction];
        }

    double DiffusionRateDifference(int src_mesh_index, int species_index, int direction)
        {
        return DiffusionRate(src_mesh_index, species_index, direction) - DiffusionRate(src_mesh_index + delta_i[direction], species_index, opposed_direction[direction]);
        }

    double DiffusionProp(int mesh_index, int species_index, int direction)
        {
        // #######################################################################################
        // reactions propensities for the Gillespie algorithm :
        // reference :
        // Gillespie, D. T. (1977). Exact stochastic simulation of coupled chemical reactions.
        // The Journal of Physical Chemistry, 81(25), 2340-2361. https://doi.org/10.1021/j100540a008
        //
        // for diffusion events treated as first order reactions, as describes by David Bernstein :
        // reference :
        // Bernstein, D. (2005). Simulating mesoscopic reaction-diffusion systems using the Gillespie algorithm.
        // Physical Review E, 71(4), Article 041103. https://doi.org/10.1103/PhysRevE.71.041103
        return mesh_x[mesh_index*n_species+species_index] * mesh_kd[mesh_index*n_species*6+species_index*6+direction];
        // #######################################################################################
        }

    virtual void AlgorithmSpecificInit() = 0;
    // should contain algorithm specific initialization steps, in order to avoid overwriting the constructor

    public :

    SimulationAlgorithm3DBase()
        {
        }

    virtual ~SimulationAlgorithm3DBase()
        {
        }

    void Init
    // constructor of the class
        (
        int w,                          //system width
        int h,                          //system height
        int d,                          //system depth
        int    n_species,               //number of species
        int    n_reactions,             //number of reactions
        int    n_env,                   //number of encironments
        std::vector<double> mesh_x0,    //initial state //mesh first array : [mesh [species]]
        std::vector<int>    mesh_chstt, //species chemostats //mesh first array : [mesh [species]]
        std::vector<int>    mesh_env,   //meshes environment indices
        double mesh_vol,                //volume of a mesh
        std::vector<double> k,          //reaction rates
        std::vector<double> sub,        //N*M substrate matrix
        std::vector<double> sto,        //N*M stoechiometry matrix
        std::vector<int>    r_env,      //reactions environments
        std::vector<double> D,          //reactions diffusion coefficients
        int sample_n,                   //number of sample timepoints
        std::vector<double> t_samples,  //sample timepoints
        double time_step,               //time step
        int seed                        //rng seed
        )
        {
        this->w = w;
        this->h = h;
        this->d = d;
        this->delta_i = std::vector<int>{+1, -1, +w, -w, +(w*h), -(w*h)};
        this->opposed_direction = std::vector<int>{1, 0, 3, 2, 5, 4};
        this->n_meshes = w*h*d;
        this->n_species = n_species;
        this->n_reactions = n_reactions;
        this->n_env = n_env;
        this->mesh_x = mesh_x0;
        this->mesh_chstt = mesh_chstt;
        this->mesh_env = mesh_env;
        this->mesh_vol = mesh_vol;
        this->sub = sub;
        this->sto = sto;
        this->n_samples = sample_n;
        this->t_samples = t_samples;
        this->sample_pos = 0;
        this->sample_mesh_x.clear();
        this->t = 0.0;
        this->dt = time_step;
        this->complete = false;
        Build_mesh_kr(k, r_env);
        Build_mesh_kd(D);
        this->rng = std::mt19937(seed);
        this->uiud = std::uniform_real_distribution<double> (0.0, 1.0);
        this->AlgorithmSpecificInit();
        }

    virtual bool Iterate() = 0;
    // one itetation of the simulation algorithm. Returns true if the simulation should continue. False otherwise.

    double GetProgress()
    // returns 100*t/tmax
        {
        return 100.0 * t/t_samples.back();
        }

    std::vector<std::vector<double>> & GetTrajectoryMatrix()
    // returns sample_mesh_xO
        {
        return sample_mesh_x;
        }

    int NSamples()
        {
        return n_samples;
        }

    int NSpecies()
        {
        return n_species;
        }

    int NMeshes()
        {
        return n_meshes;
        }
    };
