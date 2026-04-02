import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BuscaPacientes } from './busca-pacientes';

describe('BuscaPacientes', () => {
    let component: BuscaPacientes;
    let fixture: ComponentFixture<BuscaPacientes>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [BuscaPacientes],
        }).compileComponents();

        fixture = TestBed.createComponent(BuscaPacientes);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
